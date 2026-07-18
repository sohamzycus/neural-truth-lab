# Design Review — Readability & Visual Systems

**Team:** Apple HIG · Stripe Docs · Linear · Anthropic · DeepMind  
**Scope:** Presentation layer only — no technical changes.

## Task 1 — Page audit (summary)

| § | Eye lands on | 5-sec takeaway | Fatigue | Fix applied |
|---|--------------|----------------|---------|-------------|
| 0 | Deployable Intelligence quote | Philosophy + laws | Medium tables | Mermaid spine; web hero panel |
| 1–11 | Template h2 | Buried in matrices | High | Web-only exec summary + takeaway cards |
| Appendix | Matrix table | Traceability | Low | Unchanged |

## Implemented (web)

- **13 chapters** in nav (was 100+ subsections) — parse on `# §`
- **Chapter hero** — 3-bullet executive summary per §
- **Chapter takeaway** — dark card footer
- **Callouts** — Key Insight, Law, Decision, Warning from blockquotes
- **Mermaid** in report — philosophy, fertility, flywheel
- **Reading progress** bar — global chapter + scroll
- **Overview hero** — KPI cards + Five Laws above fold
- **Typography** — report-h1/h2, max-width 68ch, article scroll

## Report markdown (no length increase)

- §0 ascii → mermaid philosophy
- §6 chain → mermaid fertility economics  
- Closing page — sentence + visual + table + takeaway

## Remaining (optional)

- Dark mode toggle
- Collapse duplicate matrices in §2/§9 on web
- Chapter anchor deep links
