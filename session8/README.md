# Attention Evolution — ERA V5 Session 8

Interactive causal history of how attention mechanisms evolved from Bahdanau alignment to modern GQA, RoPE, MLA, DSA, and beyond.

## Submit

| Item | Link |
|------|------|
| **Live app** | https://attention-evolution-erav5.netlify.app |
| **GitHub** | https://github.com/sohamzycus/neural-truth-lab/tree/main/session8 |
| **Chronology data** | `web/src/data/chronology.ts` |
| **Source audit (in-app)** | Scroll to **Source Audit** — full table + assignment checklist |

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

## Chronology Sources

All dates are **arXiv first-submission** (or official release for community techniques), verified against primary sources — not agent summaries.

| Date | Mechanism | Authors | Source |
|------|-----------|---------|--------|
| 2014-09-01 | Bahdanau Attention | Bahdanau, Cho, Bengio | [arXiv:1409.0473](https://arxiv.org/abs/1409.0473) |
| 2017-06-12 | Scaled Dot-Product Attention | Vaswani et al. | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) |
| 2017-06-12 | Multi-Head Attention | Vaswani et al. | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) |
| 2017-06-12 | Learned Absolute Positions | Vaswani et al. | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) |
| 2017-06-12 | Sinusoidal Positions | Vaswani et al. | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) |
| 2019-01-02 | Transformer-XL | Dai et al. | [arXiv:1901.02860](https://arxiv.org/abs/1901.02860) |
| 2019-04-23 | Sparse Transformer | Child et al. | [arXiv:1904.10509](https://arxiv.org/abs/1904.10509) |
| 2019-11-20 | Multi-Query Attention (MQA) | Shazeer | [arXiv:1911.02150](https://arxiv.org/abs/1911.02150) |
| 2019-12-25 | Top-k Attention | Zhao et al. | [arXiv:1912.11637](https://arxiv.org/abs/1912.11637) |
| 2020-01-21 | Reformer | Kitaev et al. | [arXiv:2001.04451](https://arxiv.org/abs/2001.04451) |
| 2020-04-10 | Longformer (sliding window + global) | Beltagy et al. | [arXiv:2004.05150](https://arxiv.org/abs/2004.05150) |
| 2020-06-29 | Linear Attention | Katharopoulos et al. | [arXiv:2006.16236](https://arxiv.org/abs/2006.16236) |
| 2020-07-28 | BigBird | Zaheer et al. | [arXiv:2007.14062](https://arxiv.org/abs/2007.14062) |
| 2021-04-20 | RoPE | Su et al. | [arXiv:2104.09864](https://arxiv.org/abs/2104.09864) |
| 2021-11-16 | ALiBi | Press et al. | [arXiv:2108.12409](https://arxiv.org/abs/2108.12409) |
| 2022-05-27 | FlashAttention | Dao et al. | [arXiv:2205.14135](https://arxiv.org/abs/2205.14135) |
| 2023-05-23 | GQA | Ainslie et al. | [arXiv:2305.13245](https://arxiv.org/abs/2305.13245) |
| 2023-06-16 | Position Interpolation | Chen et al. | [arXiv:2306.15595](https://arxiv.org/abs/2306.15595) |
| 2023-06-16 | NTK-aware RoPE Scaling | bloc97 (community) | [Reddit thread](https://www.reddit.com/r/LocalLLaMA/comments/14mrgpr/dynamically_scaled_rope_further_increases/) |
| 2023-08-31 | YaRN | Peng et al. | [arXiv:2309.00071](https://arxiv.org/abs/2309.00071) |
| 2023-09-12 | Attention Sinks / StreamingLLM | Xiao et al. | [arXiv:2309.17453](https://arxiv.org/abs/2309.17453) |
| 2023-10-10 | Sliding Window Attention | Jiang et al. (Mistral 7B) | [arXiv:2310.06825](https://arxiv.org/abs/2310.06825) |
| 2024-05-07 | MLA | DeepSeek-AI | [arXiv:2405.04434](https://arxiv.org/abs/2405.04434) |
| 2024-06-10 | DeltaNet | Yang et al. | [arXiv:2406.06484](https://arxiv.org/abs/2406.06484) |
| 2024-12-12 | Gated DeltaNet | Yang et al. | [arXiv:2412.06464](https://arxiv.org/abs/2412.06464) |
| 2024-12-27 | DeepSeek-V3 (MLA at scale) | DeepSeek-AI | [arXiv:2412.19437](https://arxiv.org/abs/2412.19437) |
| 2025-02-16 | NSA | Yuan et al. | [arXiv:2502.11089](https://arxiv.org/abs/2502.11089) |
| 2025-12-02 | DeepSeek Sparse Attention (DSA) | DeepSeek-AI | [arXiv:2512.02556](https://arxiv.org/abs/2512.02556) |
| 2025-12-13 | DroPE | Gelberg et al. | [arXiv:2512.12167](https://arxiv.org/abs/2512.12167) |
| 2026-04-26 | Compressed Sparse Attention (CSA) | DeepSeek-AI | [arXiv:2606.19348](https://arxiv.org/abs/2606.19348) |

**Corrections applied during review:**
- Top-k was wrongly attributed to Performers (arXiv:2009.14794) → fixed to Explicit Sparse Transformer (arXiv:1912.11637).
- DroPE was wrongly linked to arXiv:2503.02658 → fixed to Sakana paper (arXiv:2512.12167).
- DeltaNet authors corrected to Yang et al. (not Schlag/Irie/Schmidhuber).
- YaRN date corrected to 2023-08-31 (arXiv submission).

**Beyond assignment minimum (bonus):** Bahdanau, MHA, Transformer-XL, Reformer, Longformer, BigBird, FlashAttention, Position Interpolation, DeepSeek-V3, NSA.

## Causal Story

Each timeline card shows:

```
what problem existed → why the mechanism changed → what became cheaper → what became worse → what the next paper fixed
```

Use the **Master Timeline** + chapter trade-off cards. The app is organized around bottlenecks (compute → position → KV memory → long context → recurrence → compression → sparsity), not a flat list of names.

## Architecture

```
session8/web/
├── src/data/chronology.ts   # 32 mechanisms, primary sources
├── src/data/chapters.ts     # 13-chapter narrative
├── src/data/scenarios.ts    # "What would you choose?" game
└── src/components/          # experiments, timeline, lab, audit
```

**Stack:** Vite + React 19 + TypeScript + Tailwind CSS 4 + Framer Motion

## Reviews

- `REVIEW_BEFORE.md`, `REVIEW_1.md`, `REVIEW_2.md`, `REVIEW_3.md`
- `SUBMISSION_READY.md`
