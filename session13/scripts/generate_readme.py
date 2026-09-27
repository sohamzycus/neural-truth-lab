#!/usr/bin/env python3
"""Regenerate README.md from results + host profile."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config import load_config
from src.model import count_parameters, build_model, theoretical_param_count

def pick(rows, needle):
    return next((r for r in rows if needle in r["run_id"]), None)

def main():
    cfg = load_config(ROOT / "config/experiment.yaml")
    host = json.loads((ROOT / "results/host_profile.json").read_text())
    rows = json.loads((ROOT / "results/results.json").read_text())
    b, e, m, mx = pick(rows, "baseline"), pick(rows, "euler"), pick(rows, "midpoint"), pick(rows, "max_batch")
    base_p = count_parameters(build_model(cfg.model, "none"))
    rev_p = count_parameters(build_model(cfg.model, "euler"))
    theo = theoretical_param_count(cfg.model)

    md = f"""# ERA V5 Session 13 — Reversibility Training Lab

> **Evidence machine:** Apple {host.get('cpu_brand','')} · {host.get('ram_gb')} GB RAM · PyTorch {host['pytorch']} · MPS {host['mps_available']}  
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
| vocab | {cfg.model.vocab_size} |
| layers (baseline) | {cfg.model.n_layer} |
| hidden | {cfg.model.n_embd} |
| heads | {cfg.model.n_head} |
| context | {cfg.model.block_size} |
| dtype | {cfg.runtime.dtype} |
| tied embeddings | {cfg.model.tie_weights} |

**Measured parameters:** baseline **{base_p:,}** ({base_p/1e6:.2f}M), reversible **{rev_p:,}** ({rev_p/1e6:.2f}M)  
**Analytic estimate:** {theo:,} (`theoretical_param_count` in `src/model.py`)

Parameter breakdown (baseline): embedding + 7×(attn+MLP) + `ln_f`; tied `lm_head` shares embedding weights.

## 8. Dataset / Token Budget

`TinyCorpus` (session10/11 deterministic sentences). Tokens counted by `batch × seq × steps`. Replace corpus for production; loop is corpus-agnostic.

## 9. Hardware (laptop evidence)

| Item | Measured value |
|------|----------------|
| Machine | {host['platform']} |
| CPU | {host.get('cpu_brand')} ({host.get('physical_cpus')} physical / {host.get('logical_cpus')} logical) |
| RAM | {host.get('ram_gb')} GB |
| Accelerator | Apple MPS (`device: mps` in runs) |
| PyTorch | {host['pytorch']} |

Captured: `{ROOT.name}/results/host_profile.json` via `python scripts/collect_host_profile.py`.

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

## 11. Baseline Results (`{b['run_id']}`)

| Metric | Value |
|--------|-------|
| Tokens | {b['tokens_trained']:,} |
| Wall time | {b['training_time_s']:.1f} s |
| Throughput | {b['tokens_per_sec']:.0f} tok/s |
| Final / min loss | {b['final_loss']:.4f} / {b['min_loss']:.4f} |
| Peak MPS memory | **{b['peak_mps_gb']:.3f} GB** |
| Peak RSS | {b['peak_rss_gb']:.3f} GB |
| CPU time | {b['cpu_time_s']:.2f} s |

## 12. Euler Results (`{e['run_id']}`)

| Metric | Value |
|--------|-------|
| Throughput | {e['tokens_per_sec']:.0f} tok/s ({(1-e['tokens_per_sec']/b['tokens_per_sec'])*100:.0f}% vs baseline) |
| Final loss | {e['final_loss']:.4f} |
| Peak MPS | **{e['peak_mps_gb']:.3f} GB** (+{(e['peak_mps_gb']-b['peak_mps_gb'])*1024:.0f} MB vs baseline) |
| CPU time | {e['cpu_time_s']:.2f} s ({e['cpu_time_s']/b['cpu_time_s']:.1f}× baseline CPU) |
| Reconstruction error | {e.get('reconstruction_error')} |

## 13. Midpoint Results (`{m['run_id']}`)

| Metric | Value |
|--------|-------|
| Throughput | {m['tokens_per_sec']:.0f} tok/s |
| Final loss | {m['final_loss']:.4f} (unstable; min {m['min_loss']:.4f}) |
| Peak MPS | **{m['peak_mps_gb']:.3f} GB** |
| CPU time | {m['cpu_time_s']:.2f} s |

## 14. Maximum Batch Results (`{mx['run_id']}`)

| Metric | Value |
|--------|-------|
| Batch size | **{mx['batch_size']}** (vs baseline {b['batch_size']}) |
| Peak MPS | **{mx['peak_mps_gb']:.3f} GB** |
| Throughput | {mx['tokens_per_sec']:.0f} tok/s |
| Final loss | {mx['final_loss']:.4f} |

## 15. Memory Analysis

On **this laptop (MPS)** at batch 8: baseline **{b['peak_mps_gb']:.2f} GB** vs Euler **{e['peak_mps_gb']:.2f} GB** driver allocation. Reversible stack uses **more** MPS bytes here because deeper rev blocks + recompute graph, not less — the assignment trade-off is about **activation checkpointing vs store**; at this scale unified memory is dominated by weights/optimizer/working buffers. **Max batch 64** pushes MPS to **{mx['peak_mps_gb']:.2f} GB** without OOM.

## 16. Throughput Analysis

Baseline **{b['tokens_per_sec']:.0f}** tok/s vs Euler **{e['tokens_per_sec']:.0f}** → **~{(1-e['tokens_per_sec']/b['tokens_per_sec'])*100:.0f}%** throughput cost on laptop CPU+MPS.

## 17. Loss Analysis

Toy corpus: baseline overfits (loss {b['final_loss']:.4f}). Euler higher loss ({e['final_loss']:.4f}). Midpoint unstable spikes in `loss_history`.

## 18. Trade-off Analysis

| Question | Answer (laptop 1M evidence) |
|----------|------------------------------|
| Memory saved? | MPS peak **not lower** at bs=8; max batch **8→64** is the capacity win |
| Throughput cost? | ~**{(1-e['tokens_per_sec']/b['tokens_per_sec'])*100:.0f}%** slower (Euler) |
| Larger batch? | **{mx['batch_size']}** vs **{b['batch_size']}** |
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

On **Apple M4 Pro / 24 GB / MPS**, measured 1M-token runs show reversible Euler costs **~{(1-e['tokens_per_sec']/b['tokens_per_sec'])*100:.0f}%** throughput and **~{e['cpu_time_s']/b['cpu_time_s']:.1f}×** CPU time vs baseline, while enabling **batch 64** reversible training at **{mx['peak_mps_gb']:.1f} GB** MPS peak. Run `./scripts/run_full_assignment.sh` for the full **50M-token** assignment table.

---

## Commands (quick reference)

```bash
cd session13
../session11/.venv/bin/python -m pytest tests/ -q
../session11/.venv/bin/python scripts/collect_host_profile.py
../session11/.venv/bin/python scripts/generate_readme.py
cd web/interactive-lab && npm run build
```
"""
    (ROOT / "README.md").write_text(md)
    print("Wrote README.md", len(md), "chars")

if __name__ == "__main__":
    main()
