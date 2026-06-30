# Neural Truth Lab — Animations

## Philosophy

Motion is **evidence**, not decoration. Every animation answers: *what changed, and why does it matter?*

- **Purposeful** — boundary morph = model learning; star drift = embedding shift
- **Interruptible** — scrubbing epoch cancels in-flight transitions
- **Performant** — prefer CSS transforms + canvas; avoid layout thrashing
- **Respectful** — honor `prefers-reduced-motion`

**Libraries:** Framer Motion (UI), canvas/requestAnimationFrame (viz), optional Motion One for lightweight tweens.

---

## Global Motion Tokens

```typescript
// animations/variants.ts
export const motionTokens = {
  duration: {
    fast: 0.15,
    normal: 0.3,
    slow: 0.6,
    dramatic: 1.2,
  },
  ease: {
    default: [0.4, 0, 0.2, 1],       // ease-out cubic
    spring: { type: 'spring', stiffness: 300, damping: 30 },
    bounce: [0.34, 1.56, 0.64, 1],
  },
};
```

---

## Landing Page

### Particle / Neural Background (`HeroAnimation`)

| Property | Spec |
|----------|------|
| Engine | Canvas 2D or R3F point cloud (lazy loaded) |
| Count | 80–120 nodes, 150–200 edges |
| Mouse | Repel radius 120px, strength 0.3, spring return |
| Idle | Slow drift (0.2px/frame), sine pulse on node opacity |
| Connections | Draw line if distance < 150px; opacity ∝ 1/distance |
| Performance | Cap at 60fps; reduce count on mobile |

### Hero Text Entrance

```
Sequence (stagger 0.1s):
  1. Title — opacity 0→1, y 24→0, duration 0.8s
  2. Subtitle — same, delay 0.15s
  3. CTA button — scale 0.95→1, delay 0.3s
```

### Lab Cards

- **Hover:** `y: -4`, `boxShadow` glow, border accent brightens, 0.25s
- **Icon:** subtle rotate `0 → 5deg` on hover
- **Stagger entrance:** cards appear `y: 20 → 0` with 0.08s stagger on scroll into view

---

## Navigation

- Header shrink on scroll: height transition 0.2s
- Active nav underline: `layoutId` shared element (Framer Motion) for smooth slide
- Progress ring: stroke-dashoffset animates on lab completion

---

## Lab Sections

### Section Reveal (scroll-triggered)

```typescript
const sectionReveal = {
  hidden: { opacity: 0, y: 32 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};
```

Use `viewport={{ once: true, margin: '-80px' }}`.

### Claim Block

- Large text: word-by-word or line fade-in (0.4s total, not slow typewriter)
- Accent quote mark: scale 0 → 1 spring

### Key Insight Card

- Final reveal: scale 0.96 → 1, opacity 0 → 1, border glow pulse once (0.6s)

---

## Decision Boundary (`DecisionBoundary`)

**The money shot animation for Labs 1 & 2.**

| Aspect | Spec |
|--------|------|
| Render | Canvas 2D: scatter points + filled contour |
| Per epoch | Crossfade or morph contour between snapshot grids (0.4s ease) |
| Scrubber | Instant jump when dragging; smooth morph on play |
| Color map | Class 0: cool (indigo), Class 1: warm (orange); boundary = white 30% opacity line |
| Points | Static; classes colored; slight hover scale on point nearest cursor |
| Training live | Update every epoch without full page flash |

### Contour Morph Algorithm

1. Store previous grid `G_prev`, target `G_next`
2. On frame: `G_interp = lerp(G_prev, G_next, t)` where `t` eases 0→1 over 400ms
3. Marching squares or precomputed SVG path interpolation

---

## Charts (Loss, Accuracy, Generalization)

### Line Draw

- D3 path `stroke-dasharray` animate on new point: 0 → full length, 0.5s
- New epoch: dot appears with scale spring; line extends

### Dual Lines (Generalization Lab)

- Train loss: solid accent
- Val loss: dashed secondary
- Gap region: filled gradient between curves; area width animates as slider moves

### Scrub Sync

Charts highlight vertical cursor at selected epoch; dim future segments.

---

## Epoch Slider

- Thumb glows during active training
- Tick marks at every 10% of epochs
- On scrub: number ticks up/down with `AnimatePresence` digit roll (optional, subtle)

---

## Neural Network View (`NeuralNetworkView`)

- Layers as columns of nodes (schematic, not full graph)
- **Signal flow:** pulse dot travels input → hidden → output on each epoch (0.8s)
- **Active layer highlight** during training step
- Lab 2: 5 layers collapse animation — layers slide together, nodes merge, label "≡ 1 layer"

---

## Weight Matrix (Lab 2)

| Phase | Animation |
|-------|-----------|
| Display W1…W5 | Heatmaps fade in staggered 0.1s each |
| Multiply | Arrows between matrices; result matrix fills cell-by-cell (0.05s/cell) |
| Collapse | 5 matrices scale down and stack; product matrix expands |
| Insight flash | "W = W5×W4×W3×W2×W1" text types in mono, 0.3s |

Heatmap color: diverging scale blue ↔ white ↔ orange.

---

## Embedding Galaxy (Lab 3)

| Aspect | Spec |
|--------|------|
| Projection update | Every 5 epochs: stars tween to new (x,y) over 1.2s ease-in-out |
| Star size | ∝ word frequency (min 4px, max 10px) |
| Star color | Category hue (animals, fruit, verbs) |
| Cluster emerge | No explicit animation — position tween reveals structure |
| Hover | Star scales 1.3×, neighbors highlight with connecting lines (opacity 0.4) |
| Similarity card | Slides in from right, 0.2s |

### Camera (optional R3F mode)

- Subtle parallax on mouse; disabled under reduced motion

---

## Training Controls

- **Play/Pause:** icon morph (Play ↔ Pause) via Framer Motion
- **Training active:** subtle pulse on border of control panel
- **Complete:** checkmark draw SVG stroke animation

---

## Replay

- Reset: viz fades to epoch 0 state (0.3s)
- Auto-replay option: play through all epochs at 4× speed

---

## Particles & Neurons (Global Accent)

- Occasional "neuron fire" flash along header connection lines (low frequency, 1 per 3s)
- Achievement unlock: particle burst from badge (12 dots, radial, 0.5s)

---

## Page Transitions

- Route change: crossfade content 0.2s; keep header fixed
- No full-page slide (feels app-like, not slideshow)

---

## Fullscreen Mode

- Viz expands with scale 0.98 → 1 and backdrop fade 0.2s
- Exit: reverse; Esc key

---

## Screenshot / Export

- Flash white overlay 0.1s on capture (camera shutter feel)
- Toast: "Saved" with slide up

---

## Reduced Motion Fallback

When `prefers-reduced-motion: reduce`:

- Disable particle canvas (static gradient background)
- Instant chart updates (no line draw)
- Decision boundary: snap to epoch frame, no morph
- Embedding stars: teleport to position
- Section reveals: opacity only, no y transform
- Disable neuron fire effects

---

## Performance Budget

| Animation | Max frame cost |
|-----------|----------------|
| Particle field | < 4ms |
| Decision boundary morph | < 8ms |
| Chart update | < 2ms |
| Embedding tween (50 stars) | < 3ms |

If budget exceeded: skip morph frames, snap to target.
