# Neural Truth Lab

Experience Deep Learning. Don't Just Read About It.

Interactive browser labs for activations, depth, embeddings, and generalization — powered by TensorFlow.js.

## Quick start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Dev server troubleshooting

If the app 500s after saves with `ENOENT` / `app-build-manifest.json` errors:

1. Stop the dev server (Ctrl+C).
2. Run `npm run dev:clean` (do **not** run `npm run build` while dev is running).

This happens when Turbopack/webpack hot reload races with a stale or mixed `.next` folder (e.g. after `npm run build`).

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (stable webpack) |
| `npm run dev:clean` | Clear `.next` cache then start dev — use after build or ENOENT errors |
| `npm run dev:turbo` | Start dev with Turbopack (faster, less stable on file saves) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript check |

## Features

- Four interactive labs with live training and visualizations
- Progress tracking and achievements (stored in `localStorage`)
- Keyboard shortcuts (`?` for help, `F` fullscreen on lab pages)
- Reduced-motion support across animations
- Share lab URLs via Web Share API or clipboard

## Stack

- Next.js 15 · React 19 · TypeScript
- Tailwind CSS v4 · shadcn/ui · Framer Motion
- TensorFlow.js (client-side training)

## Deploy

Production deploy targets **Netlify** with GitHub Actions CI.

```bash
npm run build   # verify locally first
```

See [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) for Netlify setup and [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) for system overview.

Optional env: `NEXT_PUBLIC_SITE_URL` for canonical Open Graph URLs.

## Specs

See [`specs/`](./specs/) for vision, architecture, lab designs, and milestones.

## License

MIT
