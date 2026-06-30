# Neural Truth Lab — Architecture

## Overview

Single-page-application style routing via **Next.js 15 App Router**. All ML training runs client-side with **TensorFlow.js**. No API routes, no database, no auth.

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   Next.js   │  │  React 19 UI │  │  Visualization Layer │ │
│  │  App Router │──│  shadcn/ui   │──│  D3 / R3F / Canvas  │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│         │                │                    │              │
│         └────────────────┼────────────────────┘              │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │   Training Engine     │                       │
│              │   TensorFlow.js       │                       │
│              │   (main or Worker)    │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Next.js 15 (App Router) |
| UI | React 19, TypeScript |
| Styling | TailwindCSS, shadcn/ui |
| Motion | Framer Motion (+ Motion One if needed) |
| ML | TensorFlow.js |
| Charts | D3.js (custom SVG/canvas charts) |
| 3D / Particles | React Three Fiber, Three.js |
| Icons | Lucide React |

---

## Route Map

| Route | Page |
|-------|------|
| `/` | Landing — hero, particle background, four lab cards |
| `/labs` | Lab index / overview |
| `/lab/activations` | Lab 1 — Activations |
| `/lab/depth` | Lab 2 — Depth |
| `/lab/embeddings` | Lab 3 — Embeddings |
| `/lab/generalization` | Lab 4 — Generalization |
| `/about` | About, credits, tech stack |

---

## Folder Structure

```
app/
  layout.tsx                 # Root layout, fonts, ThemeProvider
  page.tsx                   # Landing
  labs/page.tsx
  lab/
    activations/page.tsx
    depth/page.tsx
    embeddings/page.tsx
    generalization/page.tsx
  about/page.tsx
  globals.css

components/
  layout/                    # Header, Footer, Nav, LabShell
  landing/                   # HeroAnimation, LabCard, ParticleField
  labs/                      # Shared lab sections (Claim, Theory, etc.)
  visualization/             # DecisionBoundary, LossChart, etc.
  ui/                        # shadcn primitives

hooks/
  useTraining.ts             # Generic TF.js training loop
  useEpochHistory.ts         # Snapshot history for scrubber
  useKeyboardShortcuts.ts
  useFullscreen.ts
  useProgress.ts               # Lab completion / achievements

lib/
  utils.ts                   # cn(), formatters
  constants.ts               # Shared hyperparams defaults
  export-image.ts            # Canvas → PNG download

datasets/
  concentric-rings.ts          # Lab 1 & 2 dataset generator
  synthetic-language.ts      # Lab 3 corpus + templates
  noisy-classification.ts    # Lab 4 dataset by size

training/
  models/
    linear-classifier.ts
    mlp.ts
    embedding-lm.ts
    large-mlp.ts
  optimizers.ts
  metrics.ts                 # accuracy, confusion matrix
  weight-collapse.ts         # Lab 2 matrix multiply demo
  worker/                    # Optional Web Worker bundle

visualization/
  decision-boundary.ts       # Grid inference + contour
  embedding-projection.ts    # PCA / t-SNE wrappers
  chart-scales.ts            # D3 scale helpers

animations/
  variants.ts                # Framer Motion variants
  particles.ts               # Particle system config

types/
  training.ts                # EpochSnapshot, ModelConfig, etc.
  lab.ts                     # Lab metadata, progress

public/
  fonts/
  og-image.png
```

---

## Data Flow — Training Labs (1, 2, 4)

```
DatasetGenerator
      │
      ▼
ModelBuilder (TF.js layers)
      │
      ▼
TrainingLoop ──onEpochEnd──► EpochSnapshot[]
      │                            │
      │                            ├── DecisionBoundary (grid predictions)
      │                            ├── LossChart / AccuracyChart
      │                            └── EpochSlider (scrub index)
      ▼
Metrics (loss, accuracy, confusion matrix)
```

### EpochSnapshot (shared type)

```typescript
interface EpochSnapshot {
  epoch: number;
  loss: number;
  accuracy: number;
  validationLoss?: number;
  validationAccuracy?: number;
  weights?: tf.Tensor[];           // Lab 2 only
  decisionGrid?: Float32Array;     // flattened N×N grid
  embeddings?: Float32Array;       // Lab 3 only
  confusionMatrix?: number[][];
}
```

---

## Data Flow — Embedding Lab (3)

```
SyntheticLanguageCorpus
      │
      ▼
TokenEncoder (vocab, sequences)
      │
      ▼
EmbeddingModel (Embedding + Dense softmax)
      │
      ▼
TrainingLoop ──every N epochs──► EmbeddingSnapshot[]
      │
      ▼
PCA / t-SNE projection ──► EmbeddingGalaxy (2D positions)
      │
      ▼
Hover ──► SimilarityCard (cosine, neighbors)
```

---

## Component Architecture

### Layout Shell

- `LabShell` — wraps every lab: hero, section slots, progress rail, keyboard hint bar
- `Section` — consistent spacing, `id` anchors for in-page nav

### Shared Visualization Components

| Component | Responsibility |
|-----------|----------------|
| `HeroAnimation` | Landing + lab hero backgrounds |
| `DecisionBoundary` | Canvas/SVG contour from grid predictions |
| `LossChart` | D3 animated line chart |
| `AccuracyChart` | D3 animated line chart |
| `EpochSlider` | Scrub training timeline |
| `ReplayButton` | Restart training from epoch 0 |
| `NeuralNetworkView` | Schematic layer diagram |
| `WeightMatrix` | Heatmap + numeric multiply animation |
| `EmbeddingGalaxy` | 2D star field with hover |
| `SimilarityCard` | Neighbor list + cosine similarity |
| `GeneralizationGraph` | Dual train/val loss lines + gap shading |
| `DatasetGenerator` | Seed, noise, sample count controls |
| `TrainingControls` | Play / pause / step / reset |

---

## State Management

- **Local React state** for UI (sliders, play/pause).
- **`useReducer` or Zustand (only if needed)** for cross-section lab state.
- **No global server state** — progress persisted to `localStorage`.

```typescript
// lib/progress-storage.ts
interface UserProgress {
  completedLabs: string[];
  achievements: string[];
  lastVisitedLab?: string;
}
```

Prefer hooks over global store until complexity demands otherwise.

---

## Performance Strategy

| Concern | Approach |
|---------|----------|
| TF.js blocks UI | Run training in Web Worker; postMessage snapshots |
| Decision boundary grid | 100×100 default; memoize grid per snapshot |
| Heavy pages | `dynamic(() => import(...), { ssr: false })` for R3F, TF.js |
| Re-renders | `React.memo` on chart/canvas components; stable callbacks |
| Memory | `tf.tidy()` in training loops; dispose tensors after snapshot |
| Embedding projection | Run PCA every k epochs, not every step |

---

## Build & Deploy

- **Output**: `next build` → static export or Netlify Next adapter
- **Env**: None required for v1 (no secrets)
- **CI**: GitHub Actions — install, lint, typecheck, build
- **Hosting**: Netlify with `netlify.toml` (build command, publish dir)

---

## Security & Privacy

- No PII collection
- No external API calls during training
- `localStorage` only for progress (user device)

---

## Extension Points (post-v1)

- WebGPU backend for TF.js
- Additional labs (CNN, attention)
- URL-shared training configs (query params)
- Light theme
