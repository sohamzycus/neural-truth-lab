# Neural Truth Lab — UI Design

## Design North Star

Premium dark product. Glass surfaces floating over deep space. Motion communicates state — never decorates without purpose. Typography and whitespace do the heavy lifting; color accents guide attention.

**Anti-patterns:** Bootstrap cards, default shadcn stock look without customization, purple-on-white gradients, cramped controls, walls of text.

---

## Theme

### Color Palette

```css
/* Semantic tokens — implement in globals.css / Tailwind theme */

--background:        #0a0a0f;      /* near-black blue */
--background-elevated: #12121a;
--surface:             rgba(255, 255, 255, 0.04);
--surface-hover:       rgba(255, 255, 255, 0.07);
--border:              rgba(255, 255, 255, 0.08);
--border-strong:       rgba(255, 255, 255, 0.14);

--text-primary:        #f4f4f5;
--text-secondary:      #a1a1aa;
--text-muted:          #71717a;

--accent-primary:      #6366f1;      /* indigo */
--accent-secondary:    #8b5cf6;      /* violet */
--accent-glow:         rgba(99, 102, 241, 0.35);

--success:             #22c55e;
--warning:             #f59e0b;
--error:               #ef4444;

--gradient-hero:       linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
--gradient-surface:    linear-gradient(180deg, rgba(99,102,241,0.08) 0%, transparent 100%);
```

### Lab Accent Colors (card borders, section highlights)

| Lab | Accent |
|-----|--------|
| Activations | `#f97316` (orange) |
| Depth | `#06b6d4` (cyan) |
| Embeddings | `#a855f7` (purple) |
| Generalization | `#10b981` (emerald) |

---

## Typography

| Role | Font | Size / Weight |
|------|------|---------------|
| Display (hero) | Geist Sans or Inter | 56–72px / 700, tracking -0.02em |
| H1 (lab title) | Same | 40–48px / 600 |
| H2 (section) | Same | 24–28px / 600 |
| Body | Same | 16px / 400, line-height 1.6 |
| Label / UI | Same | 13–14px / 500, uppercase optional for section tags |
| Mono (metrics) | Geist Mono or JetBrains Mono | 14px — loss, epoch, matrix values |

**Rule:** Max ~2 sentences per theory block. Use bullet chips for theory points.

---

## Glassmorphism

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}
```

Use glass panels for: control sidebars, metric cards, floating insight callouts. Never stack more than 2 glass layers deep.

---

## Spacing & Layout

- **Max content width:** 1280px (`max-w-7xl`)
- **Section vertical rhythm:** 80–120px between major sections
- **Grid:** 12-column; labs use 8/4 or 7/5 split (viz / controls)
- **Border radius:** 12px controls, 16px panels, 24px hero cards

---

## Navigation

### Global Header (sticky, glass)

```
[Logo: Neural Truth Lab]     Labs ▾    About          [Progress ring] [Fullscreen]
```

- **Logo** → `/`
- **Labs** → dropdown or `/labs` with four cards
- **Progress ring** — % labs completed (subtle, not gamified clutter)
- Shrinks on scroll (height 64px → 48px)

### Lab In-Page Nav (sticky sub-nav below header)

Anchor links: Claim · Theory · Experiment · Results · Insight

Active section highlighted with accent underline + scroll spy.

### Footer (minimal)

Tech stack badges, GitHub link, "Built with TensorFlow.js", license.

---

## Landing Page Layout

```
┌────────────────────────────────────────────────────────┐
│  [Particle / neural canvas — full viewport, mouse repel] │
│                                                        │
│              Neural Truth Lab                          │
│         Experience Deep Learning                       │
│                                                        │
│            [ Start Experiment → ]                      │
│                                                        │
└────────────────────────────────────────────────────────┘
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Activations│ │  Depth  │ │Embeddings│ │Generalize│
│  card     │ │  card    │ │  card    │ │  card    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### Lab Cards

- Glass panel, lab accent left border (4px)
- Icon (Lucide), title, one-line description
- Hover: lift `translateY(-4px)`, glow border, icon pulse
- Click → lab route

---

## Lab Page Layout

```
┌─ Hero (compact, lab accent gradient) ─────────────────┐
│  Lab 01 · Activations                                  │
│  Activations Exist for a Reason                          │
└────────────────────────────────────────────────────────┘

┌─ Claim ───────────────────────────────────────────────┐
│  Large quote-style statement                           │
└────────────────────────────────────────────────────────┘

┌─ Theory (3–4 visual chips, no paragraph) ─────────────┐

┌─ Experiment ──────────────────────────────────────────┐
│  ┌─────────────────────┐  ┌─────────────────────────┐ │
│  │   Visualization      │  │  Controls (glass)     │ │
│  │   (decision boundary,  │  │  Train / Reset          │ │
│  │    charts, galaxy)     │  │  Epoch slider           │ │
│  │                        │  │  Hyperparams            │ │
│  └─────────────────────┘  └─────────────────────────┘ │
└────────────────────────────────────────────────────────┘

┌─ Training Progress ───────────────────────────────────┐
│  Loss chart │ Accuracy │ Confusion matrix │ Epoch N/M  │
└────────────────────────────────────────────────────────┘

┌─ Key Insight (highlight card) ────────────────────────┐

┌─ Replay + Share + Download PNG ───────────────────────┘
```

---

## Design System Components (shadcn customized)

| Primitive | Customization |
|-----------|---------------|
| Button | Primary: gradient fill; Secondary: glass outline |
| Slider | Accent track; epoch slider shows tick marks |
| Card | Glass variant default |
| Tabs | Used for model A/B comparison (Lab 1) |
| Tooltip | Dark glass, mono values |
| Badge | Lab number, achievement chips |
| Dialog | Fullscreen viz mode |
| Progress | Thin accent bar for training epoch |

### Button Hierarchy

1. **Primary** — "Start Training", "Start Experiment" (gradient)
2. **Secondary** — "Reset", "Replay" (glass outline)
3. **Ghost** — icon-only (download, share, fullscreen)

---

## Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `lg` (1024px+) | Side-by-side viz + controls |
| `md` (768px) | Stacked; controls below viz |
| `sm` (<768px) | Simplified charts; touch-friendly sliders |

Labs are **desktop-first**. Mobile shows simplified static final frame + "Best on desktop" hint.

---

## Iconography

Lucide icons, 20px UI / 24px cards:

- Activations: `Zap`
- Depth: `Layers`
- Embeddings: `Sparkles` or `Orbit`
- Generalization: `TrendingUp`
- Training: `Play`, `Pause`, `RotateCcw`
- Export: `Download`, `Share2`, `Maximize`

---

## Accessibility

- WCAG AA contrast on text (4.5:1 minimum on `--text-primary`)
- All interactive controls keyboard-focusable with visible ring (`ring-accent`)
- `prefers-reduced-motion`: disable particles, shorten transitions to 0.01ms
- Charts: `aria-label` summaries; live region for epoch/loss updates
- Skip link: "Skip to experiment"

---

## Achievement & Progress UI

- Subtle toast on lab completion (glass, auto-dismiss)
- Achievements panel (slide-over): icons + one-line unlock description
- No intrusive modals mid-training

---

## Empty & Loading States

| State | Treatment |
|-------|-----------|
| Pre-train | Viz shows dataset only; pulsing "Press Train" hint |
| Training | Progress bar + epoch counter; viz updates live |
| Complete | Insight card animates in; replay CTA visible |
| Error | Inline red glass banner; retry button |
