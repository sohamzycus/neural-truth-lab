# Lab 2 — Depth Without Nonlinearity

**Route:** `/lab/depth`  
**Lab ID:** `depth`  
**Accent:** Cyan `#06b6d4`

---

## Claim

> Stacking linear layers does not add expressive power. Five linear layers collapse into one.

---

## Theory (Visual Chips)

1. **Matrix multiplication** of linear layers equals a single matrix.
2. **Depth alone** does not create nonlinearity.
3. **Activations between layers** are what make depth meaningful.
4. **W = W₅ × W₄ × W₃ × W₂ × W₁** — same as one layer.

---

## Dataset

Same as Lab 1: **300 noisy concentric rings** (`datasets/concentric-rings.ts`).

Identical seed default (42) for consistency across labs.

---

## Models (Three Variants)

Train three models on the same data. User can run all three sequentially or compare after training.

### Model 1 — Single Linear Layer

```
Input(2) → Dense(1, sigmoid)
```

### Model 2 — Five Linear Layers (No Activation)

```
Input(2) → Dense(8, linear) → Dense(8, linear) → Dense(8, linear) → Dense(8, linear) → Dense(1, sigmoid)
```

- **No activations** between hidden layers
- 5 weight matrices: W1…W5

### Model 3 — Five Layers with ReLU

```
Input(2) → Dense(8, relu) → Dense(8, relu) → Dense(8, relu) → Dense(8, relu) → Dense(1, sigmoid)
```

- ReLU between each hidden layer

### Shared Hyperparameters

| Param | Default |
|-------|---------|
| Optimizer | Adam, lr = 0.03 |
| Epochs | 100 |
| Batch size | 32 |
| Hidden units | 8 per layer (Models 2 & 3) |

---

## Interactive Experiment

### Controls

| Control | Behavior |
|---------|----------|
| **Train Model** | Dropdown or tabs: 1-Layer / 5-Linear / 5-ReLU |
| **Compare All** | Train all three back-to-back, show results grid |
| **Show Weight Collapse** | Toggle weight matrix visualization (Model 2) |
| **Epoch slider** | Scrub decision boundary timeline |
| **Seed** | Regenerate rings |

### Weight Collapse Demo (Model 2 only)

After training (or at any epoch):

1. Extract W1, W2, W3, W4, W5 as 2D arrays
2. Display 5 heatmaps labeled W1…W5
3. Compute **W_combined = W5 × W4 × W3 × W2 × W1** numerically
4. Animate: five matrices slide together → collapse → single W_combined heatmap
5. Show formula: `W = W5 × W4 × W3 × W2 × W1`
6. Optional: compare W_combined output vs Model 1 weights — numerically equivalent decision boundary

**Module:** `training/weight-collapse.ts`

---

## Visualizations

### 1. Decision Boundary (×3 comparison)

Grid layout after "Compare All":

```
┌─────────────┬─────────────┬─────────────┐
│ 1 Linear    │ 5 Linear    │ 5 ReLU      │
│ boundary    │ boundary    │ boundary    │
└─────────────┴─────────────┴─────────────┘
```

- Models 1 & 2 boundaries should be **nearly identical** (both fail on rings)
- Model 3 boundary **curves** around rings

### 2. Loss & Accuracy Charts

- Three lines (color-coded per model)
- Toggle visibility per model

### 3. Weight Matrix Panel (`WeightMatrix`)

- Heatmaps for W1…W5
- Animated matrix multiply (`WeightMatrix` + collapse animation)
- Numeric dimensions shown: e.g. `W1: 2×8`, `W2: 8×8`, …

### 4. Neural Network View (`NeuralNetworkView`)

- Schematic: 5 layers vs 1 layer collapse animation
- Toggle: expanded stack → collapsed single layer

---

## Live Training Flow

```
For each selected model:
  epoch 1…100:
    train one epoch
    capture weights (Model 2: all Wi)
    capture decision grid snapshot
    push to history

On "Compare All":
  train Model 1 → history₁
  train Model 2 → history₂ (+ weight snapshots)
  train Model 3 → history₃
  show comparison grid at final epoch
```

---

## Money Shot

**Weight collapse animation:**

Five heatmaps merge into one. Caption appears:

> "5 layers. 0 activations. ≡ 1 linear layer."

Cut to decision boundaries: **1-Layer** and **5-Linear** look the same. **5-ReLU** does not.

---

## Key Insight

> **Depth without activation is mathematically equivalent to one layer.** ReLU is what makes depth matter.

---

## Replay

- Replay decision boundary evolution per model
- Replay weight collapse animation independently
- Download comparison PNG (3-panel boundary)

---

## Acceptance Criteria

- [ ] Three models train successfully on ring dataset
- [ ] Model 1 and Model 2 achieve similar (~50%) accuracy and similar linear boundaries
- [ ] Model 3 achieves >95% accuracy with curved boundary
- [ ] Weight matrices W1…W5 displayed as heatmaps
- [ ] W_combined computed correctly and collapse animation plays
- [ ] Neural network collapse schematic animates
- [ ] Epoch scrubber works per model
- [ ] Key insight card on completion
- [ ] Lab marked complete in progress

---

## Component Map

| Section | Components |
|---------|------------|
| Experiment | `DecisionBoundary` ×3, `NeuralNetworkView` |
| Weights | `WeightMatrix`, collapse animation |
| Progress | `LossChart`, `AccuracyChart`, `EpochSlider` |
| Insight | Highlight card + `ReplayButton` |

---

## Copy (UI Strings)

| Element | Text |
|---------|------|
| Hero title | Depth Without Nonlinearity |
| Hero subtitle | Lab 02 · Why depth needs activation |
| Model 1 | 1 Linear Layer |
| Model 2 | 5 Linear Layers |
| Model 3 | 5 Layers + ReLU |
| Collapse caption | Five layers collapse into one. |
| Final statement | Depth without activation is mathematically equivalent to one layer. |

---

## Edge Cases

- **Numerical precision:** W product may differ slightly from Model 1 weights due to training path; boundary equivalence is the visual proof, not weight equality
- **Large matrices on mobile:** hide numeric cells, show heatmap only
- **Training time:** 3 sequential runs ~3× single lab; show progress "Training model 2 of 3…"
