# ERA V5 Session 13 — Reversibility Lab

## The question

Can I trade compute for memory when training a small language model?

I trained the same ~20M-parameter causal LM twice: once normally, once with reversible blocks (Euler and Midpoint). I ran everything on my laptop. I logged throughput, loss, CPU time, and MPS driver memory.

## The experiment

- **Target:** 50M tokens (`config/experiment.yaml`)
- **Recorded smoke runs:** 1M tokens each (baseline, Euler, Midpoint, max-batch sweep)
- **Artifacts:** `results/results.json`, `results/host_profile.json`, `results/plots/`
- **Code:** `src/` · **UI:** `web/interactive-lab/`

## My machine

Captured 2026-09-27 on this host (`results/host_profile.json`):

| | |
|---|---|
| CPU | Apple M4 Pro, 12 cores |
| RAM | 24 GB unified |
| Accelerator | Apple MPS |
| PyTorch | 2.14.0 |

## What I expected

At batch 8, I expected reversible training to show **lower** peak MPS memory than the normal model. Same batch, same token budget, less activation storage.

## What actually happened

At batch 8, **it did not.**

| | Normal | Euler |
|---|---|---|
| Throughput | 18,834 tok/s | 6,609 tok/s |
| Peak MPS | **1.09 GB** | **1.32 GB** |
| CPU time | 8.60 s | 61.64 s |

Euler used **more** measured driver memory at the same batch, and a lot more CPU time. I did not hide that in the UI or this doc.

The story that held up on this machine was **batch capacity**: I could push the reversible Euler run to **batch 64** (peak **4.93 GB** MPS) without OOM in the max-batch sweep.

## Run 01 — Baseline

```bash
python -m src.experiment --mode baseline --tokens 1000000 --run-label baseline_1M_laptop
```

- 19,755,456 parameters
- Batch 8, seq 256
- **18,834 tok/s**, final loss **0.0180**
- Peak MPS **1.089 GB**, CPU **8.60 s**

## Run 02 — Euler

Same batch size. Reversible Euler.

- **6,609 tok/s**, final loss **3.2618**
- Peak MPS **1.323 GB** (higher than baseline)
- CPU **61.64 s**
- Reconstruction error **~4.77e-7**

## Run 03 — Midpoint

I wanted to compare integrators. Midpoint reconstruction error was **~0.13** in block tests, and the **loss curve blew up** mid-run (spikes above 200 in `loss_history`). Final loss **36.99** in this run.

- **6,354 tok/s**, CPU **62.96 s**
- I would not call this variant “stable” in this setup.

## Run 04 — Maximum batch

I swept batch size for reversible Euler until the runner found a large stable batch on MPS.

- **Batch 64**
- **6,817 tok/s**, final loss **4.2662**
- Peak MPS **4.934 GB**

## The surprising result

I expected less memory at batch 8. I got the opposite on MPS driver allocation.

So I changed the question: **how large a batch can I run?** That is where reversibility mattered *practically* on this laptop—not a lower number at bs=8.

## Memory vs compute

- **Compute:** Euler ~**7×** more CPU time than baseline for the 1M run.
- **Throughput:** ~**65%** slower than baseline at batch 8.
- **Memory (measured):** not lower at batch 8; larger batch run shows **4.93 GB** peak at bs=64.

The reversible design is about **what you store vs what you recompute**. On Apple MPS, `driver_allocated_memory` also reflects weights, graphs, and runtime—not activations alone.

## What the numbers say

All values below are from `results/results.json` (1M-token runs, MPS):

| Run | Batch | tok/s | Final loss | Peak MPS | CPU s |
|-----|-------|-------|------------|----------|-------|
| baseline_1M_laptop | 8 | 18834 | 0.0180 | 1.089 GB | 8.60 |
| euler_1M_laptop | 8 | 6609 | 3.2618 | 1.323 GB | 61.64 |
| midpoint_1M_laptop | 8 | 6354 | 36.9894 | 1.323 GB | 62.96 |
| max_batch_64 | 64 | 6817 | 4.2662 | 4.934 GB | 12.12 |

## What failed

- Midpoint training instability on the toy corpus with this rev stack.
- My initial mental model (“reversible ⇒ lower peak at bs=8”) on MPS.

## Netlify hosting

Git-connected deploy: base directory **`session13/web/interactive-lab`** — details in `web/interactive-lab/NETLIFY.md`.

## Interactive Lab

```bash
cd session13/web/interactive-lab
npm install
npm run dev
```

Static build (no backend required): loads `/data/results.json` and `/data/host_profile.json`. Sliders are **estimated**; recorded runs are **measured** (badges in UI).

## Evidence

- `results/results.json` — metrics + loss history
- `results/host_profile.json` — laptop snapshot
- `results/plots/` — loss PNGs from `scripts/generate_plots.py`
- Terminal-style panels in the UI render **recorded** CLI output, not fake screenshots

## Reproduce the experiment

```bash
cd session13
pip install -r requirements.txt
python scripts/collect_host_profile.py
pytest tests/ -q
python -m src.experiment --mode baseline --tokens 1000000 --run-label baseline_1M_laptop
python -m src.experiment --mode euler --tokens 1000000 --run-label euler_1M_laptop
python -m src.experiment --mode midpoint --tokens 1000000 --run-label midpoint_1M_laptop
python -m src.experiment --mode max_batch --tokens 1000000
./scripts/run_full_assignment.sh   # 50M tokens — ~7h on this machine
```

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `notebooks/01_baseline_20m_50m.ipynb` | Normal training |
| `notebooks/02_reversible_euler.ipynb` | Euler |
| `notebooks/03_reversible_midpoint.ipynb` | Midpoint |
| `notebooks/04_reversible_max_batch.ipynb` | Max batch |

Colab: clone repo, `pip install -r requirements.txt`, set `tokens=50_000_000` in the notebook cell.

## Results

Full 50M-token table: run `./scripts/run_full_assignment.sh` and regenerate README with `python scripts/generate_readme.py` if you want tables auto-filled from JSON.

## What I learned

- I expected lower memory at batch 8. I didn’t get it on this MPS measurement.
- Euler was stable enough to keep going.
- Midpoint was not trustworthy in this run.
- The practical win here was **batch 8 → 64**, not a smaller peak at bs=8.
- Reversibility cost a lot of throughput. That trade-off is the point.

## Limitations

- One laptop, one corpus, 1M-token recorded runs (50M configured but not the default artifact in this README).
- MPS `driver_allocated_memory` ≠ activation-only VRAM accounting.
- I would not generalize these numbers to CUDA or larger models without re-measuring.

## Next experiment

- 50M-token full runs on this machine or a CUDA box.
- Separate activation-only accounting if the platform exposes it.
- Fix or drop Midpoint for this architecture after reviewing the inverse step.
