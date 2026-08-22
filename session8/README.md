# Attention Evolution — ERA V5 Session 8

Interactive causal history of how attention mechanisms evolved from Bahdanau alignment to modern GQA, RoPE, MLA, and beyond.

## Live URL

https://attention-evolution-session8.netlify.app

Netlify dashboard: https://app.netlify.com/projects/attention-evolution-session8

## GitHub

https://github.com/sohamzycus/neural-truth-lab/tree/main/session8

## How to Run Locally

```bash
cd session8/web
npm install
npm run dev
```

Open http://localhost:5173

### Verify

```bash
npm run build
npm test
npm run lint
```

## Architecture

```
session8/web/
├── src/
│   ├── data/
│   │   ├── chronology.ts    # Primary-source timeline (27 mechanisms)
│   │   ├── chapters.ts      # 13-chapter narrative structure
│   │   └── scenarios.ts       # "What would you choose?" game
│   ├── components/
│   │   ├── experiments/     # Interactive demos (QKV, mask, O(n²), KV cache, RoPE, etc.)
│   │   ├── timeline/        # Master timeline, pressure bar, family tree
│   │   ├── lab/             # Architecture builder
│   │   ├── game/            # Scenario reasoning game
│   │   ├── modes/           # 60-second tour, beginner/expert
│   │   └── audit/           # Source audit table
│   ├── context/             # Global app state (mode, chapter, timeline selection)
│   └── lib/                 # Math utilities (softmax, KV cache sizing)
└── public/
```

**Stack:** Vite + React 19 + TypeScript + Tailwind CSS 4 + Framer Motion

## Chronology Sources

All entries in `src/data/chronology.ts` include:

| Field | Purpose |
|-------|---------|
| `date` | First public release (arXiv submission or venue) |
| `sourceType` | PRIMARY PAPER, CONFERENCE PAPER, TECHNICAL REPORT, COMMUNITY ORIGIN |
| `sourceUrl` | Direct link to primary source |
| `buys` / `givesUp` / `chooseWhen` | Honest trade-off cards |

**Community technique labeled:** NTK-aware RoPE scaling (bloc97, Reddit 2023).

See the in-app **Source Audit** section for the full table.

## Interactive Experiments

| Experiment | Teaches |
|------------|---------|
| Opening sequence | Q×Kᵀ → softmax → V pipeline; scale problem |
| Bank disambiguation | Context changes representation, not token |
| Q/K/V experiment | Query-driven attention weights → equation |
| Causal masking | Why autoregressive models lock future tokens |
| O(n²) slider | Pairwise cost growth (128 → 1T) |
| KV cache simulator | MHA/GQA/MQA memory during decode |
| RoPE visualization | Rotation encodes relative position in QᵀK |
| Position story | Learned → sinusoidal → RoPE → ALiBi → DroPE |
| Context extension | PI → NTK-aware → YaRN |
| FlashAttention IO | Algorithm vs hardware efficiency |
| Attention sinks | StreamingLLM sink tokens |
| DeltaNet memory | Delta-rule associative update (conceptual) |
| MLA compression | Latent KV compression |
| Architecture lab | Compose choices, see trade-offs |
| Scenario game | 8 workloads, reason then reveal |
| 60-second mode | Guided compressed narrative |
| Beginner/Expert toggle | Progressive depth |

## Known Limitations

- Greenfield build (no prior session8 code existed)
- O(n²) matrix uses canvas approximation, not millions of DOM nodes
- DeltaNet demo is labeled conceptual, not neural implementation
- Some chronology dates are arXiv first-submission dates; venue dates may differ slightly
- Benchmark Replit app was unreachable during development
- Live Netlify URL pending deployment

## Reviews

- `REVIEW_BEFORE.md` — pre-implementation audit
- `REVIEW_1.md` — student reviewer
- `REVIEW_2.md` — ML researcher reviewer
- `REVIEW_3.md` — design critic reviewer
- `SUBMISSION_READY.md` — final verification checklist
