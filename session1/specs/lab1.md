# Lab 1 — Activations Exist for a Reason

**Route:** `/lab/activations`  
**Lab ID:** `activations`  
**Accent:** Orange `#f97316`

---

## Claim

> Without nonlinearity, a neural network cannot separate concentric rings — no matter how you train it.

---

## Theory (Visual Chips)

Display as 3–4 chips, not paragraphs:

1. **Linear layers** compose into a single linear transformation.
2. **Activation functions** introduce nonlinearity between layers.
3. **Nonlinearity** lets the model bend decision boundaries around curved data.
4. **Same data + same depth** — only activation changes the outcome.

Optional micro-diagram: `Linear → Linear = Linear` vs `Linear → ReLU → Linear = Curved`.

---

## Dataset

| Parameter | Value |
|-----------|-------|
| Type | 2D noisy concentric rings (binary classification) |
| Samples | 300 (150 inner, 150 outer) |
| Inner ring radius | ~0.5 ± noise |
| Outer ring radius | ~1.0 ± noise |
| Noise | Gaussian σ = 0.15 |
| Features | x, y (normalized to [-1, 1]) |
| Seed | User-adjustable (default 42) |

**Generator:** `datasets/concentric-rings.ts`

```typescript
interface RingDataset {
  features: Float32Array;  // [N, 2]
  labels: Float32Array;  // [N] 0 | 1
  metadata: { inner: number; outer: number; noise: number };
}
```

---

## Models

Train **two models in parallel** on the **same dataset**, **same optimizer**, **same epochs**. Only architecture/activation differs.

### Model A — Linear Stack

```
Input(2) → Dense(16, linear) → Dense(1, sigmoid)
```

- Hidden activation: **none** (linear)
- Output: sigmoid (binary cross-entropy)

### Model B — With ReLU

```
Input(2) → Dense(16, relu) → Dense(1, sigmoid)
```

- Hidden activation: **ReLU**
- Same 16 hidden units

### Shared Hyperparameters

| Param | Default |
|-------|---------|
| Optimizer | Adam, lr = 0.03 |
| Epochs | 100 |
| Batch size | 32 |
| Loss | binaryCrossentropy |
| Metric | accuracy |

---

## Interactive Experiment

### Controls (`TrainingControls`)

| Control | Behavior |
|---------|----------|
| **Train Both** | Starts parallel training A + B |
| **Reset** | Reinitialize weights, clear history |
| **Epoch slider** | Scrub timeline 0…100 |
| **Seed** | Regenerate dataset |
| **Learning rate** | Slider 0.001–0.1 (advanced, collapsed by default) |

### Layout

Split view or tabs:

- **Side-by-side** decision boundaries (recommended): Model A left, Model B right
- Shared epoch slider controls both

---

## Visualizations

### 1. Decision Boundary (`DecisionBoundary`)

- Grid: 100×100 over [-1.2, 1.2]²
- Infer each cell → class probability → contour at 0.5
- Overlay scatter: inner ring (accent cool), outer ring (accent warm)
- **Animate every epoch** — morph between snapshots
- Scrubber jumps to any epoch instantly

### 2. Loss Chart (`LossChart`)

- Two lines: Model A (muted), Model B (accent)
- X: epoch, Y: loss (log scale optional toggle)

### 3. Accuracy Chart (`AccuracyChart`)

- Same dual-line pattern

### 4. Confusion Matrix

- 2×2 per model (compact, side-by-side)
- Update on scrub

### 5. Training Progress Bar

- Epoch N / 100, elapsed time

---

## Live Training Flow

```
1. User clicks "Train Both"
2. For epoch 1…100:
   a. Train Model A one epoch → snapshot A
   b. Train Model B one epoch → snapshot B
   c. Push to epochHistory[]
   d. Update viz (non-blocking; yield to UI)
3. On complete → reveal Key Insight card
```

Use `tf.tidy()` per epoch. Consider Web Worker if frame drops below 30fps.

---

## Money Shot

**The moment of truth (epoch ~50–80):**

- Model A: decision boundary remains a **straight line** (or nearly linear split — fails on rings)
- Model B: boundary **wraps** around inner ring, separating concentric classes

Side-by-side at same epoch. User scrubs and sees A never curves; B does.

---

## Key Insight

> **Nothing changed except ReLU.** Same data. Same optimizer. Same epochs. Same hidden size. Nonlinearity is the difference between failure and perfect separation.

Display in highlight card with orange left border. Animate in on training complete.

---

## Replay

- **Replay** button: auto-scrub epochs 0→100 at 4× speed
- **Download PNG**: export side-by-side boundary snapshot
- **Share**: copy URL with `?epoch=75` query param (optional v1.1)

---

## Success Metrics (User Understanding)

After completing the lab, user should answer:

1. Why can't a linear model separate rings?
2. What does ReLU enable that linear cannot?

---

## Acceptance Criteria

- [ ] Dataset regenerates with seed control
- [ ] Both models train to completion without UI freeze
- [ ] Decision boundaries animate per epoch
- [ ] Epoch slider scrubs both models synchronously
- [ ] Model A accuracy plateaus ~50%; Model B reaches >95%
- [ ] Confusion matrix reflects poor vs good separation
- [ ] Key insight card appears on completion
- [ ] Replay and PNG export work
- [ ] Lab marked complete in progress storage

---

## Component Map

| Section | Components |
|---------|------------|
| Hero | `LabShell`, lab accent gradient |
| Experiment | `DecisionBoundary` ×2, `DatasetGenerator` |
| Progress | `LossChart`, `AccuracyChart`, confusion matrix, `EpochSlider` |
| Insight | Insight card + `ReplayButton` |

---

## Copy (UI Strings)

| Element | Text |
|---------|------|
| Hero title | Activations Exist for a Reason |
| Hero subtitle | Lab 01 · Nonlinearity |
| CTA | Train Both Models |
| Model A label | Linear (no activation) |
| Model B label | ReLU Hidden Layer |
| Final statement | Nothing changed except ReLU. |
