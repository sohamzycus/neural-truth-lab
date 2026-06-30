# Lab 4 — Generalization Arena

**Route:** `/lab/generalization`  
**Lab ID:** `generalization`  
**Accent:** Emerald `#10b981`

---

## Claim

> More data closes the gap between what a model memorizes and what it truly learns.

---

## Theory (Visual Chips)

1. **Training loss** measures fit on seen data.
2. **Validation loss** measures fit on unseen data.
3. **Generalization gap** = train loss − val loss (or val − train depending on convention; display as shaded region between curves).
4. **More data** → model can't memorize → must learn general patterns → gap shrinks.

---

## Dataset

**Learnable noisy classification** — 2D input, binary or multi-class output.

| Parameter | Value |
|-----------|-------|
| Type | Non-linear boundary (e.g. moons, circles, or XOR-like with noise) |
| Noise | Label noise 5–10% + feature noise σ = 0.1 |
| Features | 2D |
| Train/Val split | 80/20 from generated pool |

**Module:** `datasets/noisy-classification.ts`

### Train Size Variants

User selects dataset size via slider (discrete stops):

| Size | Label |
|------|-------|
| 20 | Tiny |
| 200 | Small |
| 2000 | Medium |
| 20000 | Large |

For each size: generate N samples, split train/val, train a **fresh model** (or cache results for instant slider feedback — see below).

---

## Model

**Large neural network** relative to data size (to encourage overfitting on small data):

```
Input(2) → Dense(64, relu) → Dense(64, relu) → Dense(32, relu) → Dense(1, sigmoid)
```

| Parameter | Default |
|-----------|---------|
| Optimizer | Adam, lr = 0.001 |
| Epochs | 150 |
| Batch size | min(32, train_size / 2) |
| Regularization | None (intentionally — show overfitting) |

**Module:** `training/models/large-mlp.ts`

---

## Interactive Experiment

### Primary Control — Dataset Size Slider

```
[ 20 ]──────[ 200 ]──────[ 2000 ]──────[ 20000 ]
         Tiny    Small     Medium      Large
```

**Behavior options (pick one for v1):**

**Option A — Train on demand (simpler):**  
User picks size → clicks Train → model trains → results display.

**Option B — Pre-cache (smoother UX):**  
On lab load, train all 4 sizes in background (or sequentially with progress). Slider instantly shows cached curves. Recommended for demo polish.

### Secondary Controls

| Control | Behavior |
|---------|----------|
| **Train** | Train at current slider size |
| **Train All Sizes** | Batch train 20, 200, 2000, 20000 |
| **Epoch slider** | Scrub within current size's history |
| **Seed** | Regenerate dataset |

---

## Visualizations

### 1. Generalization Graph (`GeneralizationGraph`)

Dual-line chart:

- **Train loss** — solid emerald line
- **Validation loss** — dashed muted line
- **Gap shading** — filled area between curves (opacity 0.2)
- Animate on slider change: curves morph or crossfade between cached runs

### 2. Gap Metric Card

```
Generalization Gap: 0.42 → 0.03
```

Large mono number, animates count-up when size changes.

### 3. Accuracy Cards

| Metric | Train | Val |
|--------|-------|-----|
| Size 20 | 100% | 55% |
| Size 20000 | 92% | 90% |

Show train vs val accuracy side-by-side.

### 4. Decision Boundary (optional secondary)

Show overfitting on size 20: boundary wiggles to fit noise. On 20000: smoother boundary.

### 5. Dataset Scatter

Train points (filled), val points (outline), toggle visibility.

---

## Live Training Flow

```
For each dataset size S in [20, 200, 2000, 20000]:
  1. Generate dataset of size S
  2. Split train/val
  3. Initialize fresh model
  4. For epoch 1…150:
     - train on train set → train_loss, train_acc
     - evaluate on val set → val_loss, val_acc
     - push snapshot
  5. Store RunResult { size, history, finalGap }

UI slider selects RunResult → charts update
```

---

## Money Shot

**Slider animation:**

User drags from **20 → 20000**:

- Train loss stays low across sizes
- Val loss starts high (size 20), drops as size grows
- Gap shading **visibly shrinks**
- Gap number animates from ~0.4 → ~0.02

Split-screen optional: size 20 boundary (jagged, overfit) vs 20000 (smooth).

---

## Key Insight

> **Small data invites memorization. Large data forces generalization.** The gap between train and validation loss tells you which regime you're in.

---

## Replay

- Replay loss curves for current size (epoch scrub)
- Animate slider auto-play: 20 → 200 → 2000 → 20000 with 2s pause each
- Download graph PNG

---

## Acceptance Criteria

- [ ] Dataset generates at all four sizes
- [ ] Model trains without UI freeze (Worker recommended for 20000)
- [ ] Size 20: train acc ≈ 100%, val acc significantly lower, large gap
- [ ] Size 20000: train and val acc within ~5%, small gap
- [ ] Generalization graph shows dual lines + gap shading
- [ ] Slider switches between cached runs smoothly
- [ ] Gap metric animates on size change
- [ ] Key insight card on first full comparison
- [ ] Lab marked complete in progress

---

## Component Map

| Section | Components |
|---------|------------|
| Experiment | `GeneralizationGraph`, `DatasetGenerator`, size slider |
| Metrics | Gap card, accuracy cards |
| Optional | `DecisionBoundary`, scatter plot |
| Progress | `EpochSlider`, `TrainingControls` |
| Insight | Highlight card + `ReplayButton` |

---

## Copy (UI Strings)

| Element | Text |
|---------|------|
| Hero title | Generalization Arena |
| Hero subtitle | Lab 04 · Data vs memorization |
| Slider label | Training set size |
| Gap label | Generalization Gap |
| Final statement | As data grows, the gap closes. |

---

## Performance Notes

| Size | Strategy |
|------|----------|
| 20, 200 | Main thread OK |
| 2000 | Main thread with yield |
| 20000 | Web Worker strongly recommended |

Pre-caching all 4 runs on lab load may take 30–60s — show skeleton UI + "Preparing experiments…" with per-size progress.

---

## Achievements (optional)

- **Memorizer** — train at size 20, gap > 0.3
- **Scientist** — compare all 4 sizes
- **Truth Seeker** — complete all 4 labs
