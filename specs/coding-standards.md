# Neural Truth Lab — Coding Standards

## TypeScript

- **Strict mode** enabled (`strict: true` in `tsconfig.json`)
- No `any` — use `unknown` + narrowing, or proper generics
- Explicit return types on exported functions and hooks
- Prefer `interface` for object shapes; `type` for unions/intersections
- Use `satisfies` for config objects where inference helps

```typescript
// Good
export function generateRings(seed: number, count: number): RingDataset { ... }

// Avoid
export function generateRings(seed, count) { ... }
```

---

## React & Next.js

### Components

- **Server Components** by default; add `'use client'` only when needed (hooks, events, TF.js, canvas)
- One component per file; name matches export (`DecisionBoundary.tsx`)
- Props interface named `{ComponentName}Props`
- Colocate small helpers in same file; shared logic → `lib/` or `hooks/`

### Hooks

- Prefix with `use` — `useTraining`, `useEpochHistory`
- Return stable tuples or objects; memoize callbacks with `useCallback`
- Cleanup TF.js tensors in `useEffect` return

```typescript
export function useTraining(config: TrainingConfig) {
  const [state, dispatch] = useReducer(trainingReducer, initialState);
  // ...
  useEffect(() => () => { tf.disposeVariables(); }, []);
  return { state, train, reset, pause };
}
```

### Dynamic Imports

Heavy client-only modules:

```typescript
const HeroAnimation = dynamic(() => import('@/components/landing/HeroAnimation'), {
  ssr: false,
  loading: () => <HeroSkeleton />,
});
```

---

## File & Folder Conventions

| Path | Convention |
|------|------------|
| `app/` | Routes only; thin pages composing components |
| `components/ui/` | shadcn primitives (do not edit heavily — wrap instead) |
| `components/visualization/` | Canvas/D3 viz; client components |
| `hooks/` | Shared React hooks |
| `lib/` | Pure utilities, no React |
| `datasets/` | Pure data generators |
| `training/` | TF.js models and loops |
| `types/` | Shared TypeScript types |

### Naming

- Files: `kebab-case.ts` / `PascalCase.tsx` for components
- Constants: `SCREAMING_SNAKE` for true constants; `camelCase` for config objects
- CSS: Tailwind utilities; avoid custom CSS except tokens in `globals.css`

---

## TensorFlow.js

```typescript
// Always wrap training steps
tf.tidy(() => {
  const loss = model.trainOnBatch(x, y);
  return loss;
});

// Dispose snapshots when replacing
previousTensor?.dispose();
```

- Prefer `tf.sequential()` for lab models
- Set backend early: `await tf.setBackend('webgl')` with CPU fallback
- Extract weights for viz with `.arraySync()` then dispose temp tensors
- Web Worker: postMessage serializable snapshots only (Float32Array, numbers)

---

## Styling (Tailwind + shadcn)

- Use `cn()` from `lib/utils` for conditional classes
- Design tokens via CSS variables (see `ui-design.md`)
- No inline styles except canvas dimensions
- Customize shadcn theme once in `globals.css` — avoid per-component color overrides

```typescript
<div className={cn('glass-panel p-6', isTraining && 'ring-1 ring-accent-primary')} />
```

---

## Visualization (D3 + Canvas)

- D3 for scales, axes, line generators — render via React refs or direct DOM
- Canvas for decision boundaries and particle fields (performance)
- Resize with `ResizeObserver`; debounce 100ms
- Destroy D3 selections on unmount

---

## State & Data

- **No duplicated training logic** — shared `useTraining` / `runTrainingLoop`
- Dataset generators are pure functions (testable without TF.js)
- Progress persistence: `lib/progress-storage.ts` wrapping `localStorage`
- URL state for epoch scrub: optional `?epoch=50` via `useSearchParams`

---

## Error Handling

- Training errors: catch, display inline banner, log to console in dev
- TF.js backend failure: fallback message "WebGL unavailable, using CPU"
- Never silent catch — always surface user-visible message for train failures

---

## Accessibility

- Interactive elements: `aria-label`, `role` where needed
- Live regions for epoch/loss: `aria-live="polite"`
- Keyboard: Space = play/pause, R = reset, F = fullscreen, ? = shortcuts help
- Focus trap in fullscreen dialog only

---

## ESLint & Prettier

- ESLint: `eslint-config-next`, `@typescript-eslint`
- Prettier: single quotes, trailing comma es5, printWidth 100
- Run in CI: `lint`, `typecheck` (`tsc --noEmit`), `build`

```json
// .eslintrc rules emphasis
"@typescript-eslint/no-explicit-any": "error",
"@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
```

---

## Testing (v1 minimum)

- Unit tests for pure functions: dataset generators, matrix multiply collapse, cosine similarity
- No full TF.js integration tests in CI (flaky/slow) — manual QA checklist per lab
- Optional: snapshot tests for PCA on fixed embedding matrix

---

## Git & Commits

- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- One logical change per commit
- Do not commit `.env`, `node_modules`, `.next`

---

## Documentation

- JSDoc on exported utilities and hooks (one-liner description + param types)
- README: quick start, stack, deploy
- Inline comments only for non-obvious math (e.g. weight collapse order)

---

## Performance Checklist

- [ ] `React.memo` on chart/canvas components
- [ ] `useMemo` for expensive grids and projections
- [ ] `tf.tidy()` in every training step
- [ ] Web Worker for Lab 4 size 20000
- [ ] Lazy load R3F and TF.js pages
- [ ] `prefers-reduced-motion` respected everywhere

---

## Security

- No `dangerouslySetInnerHTML`
- No external script injection
- Sanitize share URLs (query params only)

---

## ponytail Comments

When taking intentional shortcuts:

```typescript
// ponytail: O(n²) neighbor search fine for vocab < 32; upgrade to spatial index if vocab grows
```

Name the ceiling and upgrade path.
