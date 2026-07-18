# REVIEW.md — Final Committee Rejection Lens

**Committee:** Jeff Dean · Noam Shazeer · Ilya Sutskever · Nandan Nilekani · Skeptical VC · ERA V5 Evaluator  
**Question only:** *What would make me reject this proposal?*  
**Fix threshold:** Critical and Major only.

---

## Critical (would reject)

| # | Criticism | Who says it |
|---|-----------|-------------|
| C1 | **Fertility 1.14 and 21% savings are derived, not measured** on India-shaped production traffic. A $100M bet on modeled inference economics fails basic empiricism. | Jeff Dean, VC |
| C2 | **No named central research idea** in the opening—evaluator remembers tables, not thesis. Reads as "excellent spec," not "new optimization philosophy." | Ilya, ERA V5 |
| C3 | **Gemma-India / Llama-Bharat would look identical** after §3: same corpora story, same 40B, unless Deployable Intelligence is stated as the *hypothesis*, not a bullet. | Shazeer, VC |
| C4 | **30M queries/day and $13M/yr savings** are assumed scale. If Year-2 volume is 3M/day, TCO argument collapses—no sensitivity kill in executive. | VC |
| C5 | **Agent recovery ≥0.70** with 55% pretrain baseline and synthetic ToolLoop—no pilot letter, no external validation. $12M alignment may buy benchmark gaming. | Dario analogue / VC |

---

## Major (conditional reject without fix)

| # | Criticism | Who says it |
|---|-----------|-------------|
| M1 | **Page 1–3 still split attention**: laws, locked decisions, deployment table, success Q&A—evaluator must synthesize; should be one causal spine. | ERA V5 |
| M2 | **Five Laws read as labels**, not physics ("Capabilities before corpus" vs "Capabilities define data"). | Ilya |
| M3 | **India-first = dataset inventory** in evaluators' memory (GST, NCERT) not **structural constraints** (GPU scarcity, code-switch cognition, SME ₹). | Nilekani |
| M4 | **§1–§11 repeat §0** without law IDs—philosophy does not propagate; chapters feel template-identical. | ERA V5 |
| M5 | **128k vocab**: Pareto is internal composite; no independent fertility measurement on target scripts at decision time. | Shazeer |
| M6 | **MCDA-7 sharpening 2.8** feels tuned to hit Hindi 17.9%—sensitivity not shown; population weighting rejection could be post-hoc. | Jeff Dean |
| M7 | **DeepSeek-class 8B** at aggressive $/M undercuts "tokenizer moat"—report does not argue why 40B foundation vs distilled router-only. | VC |
| M8 | **Judiciary/long-context** (Kanoon 2.8B, 128k) underspecified vs compound legal docs—weak defense vs longer context competitors. | ERA V5 |

---

## Minor (note, do not block)

| # | Criticism |
|---|-----------|
| m1 | Appendix A duplicates §0 locked decisions |
| m2 | §6 and §5 both state fertility causal chain |
| m3 | Benchmark names (MMLU, HumanEval) still visible in L4 monitoring—acceptable but noisy |
| m4 | COMMITTEE_REVIEW.md and REPORT_REVIEW.md overlap—consolidate in repo hygiene |
| m5 | PDF export untested on full 1,200-line doc at committee scale |

---

## Cosmetic

| # | Criticism |
|---|-----------|
| x1 | "v2.2" metadata means nothing to evaluator |
| x2 | Chapter count in web nav splits on `##` not `# §`—UX not proposal |
| x3 | Glossary could be one line in §0 |

---

## Fixes applied (Critical/Major → §0 only)

| Issue | Response |
|-------|----------|
| C2, M1, M2 | **Deployable Intelligence** named; Five Laws rewritten as fundamental statements; one causal diagram replaces three §0 tables |
| C3 | Explicit "why not Gemma-India" line in §0 |
| M3 | Observation framed as deployment constraints, not languages |
| C4 | Success metric includes TCO savings kill (<10%) |

**Not fixed in this pass (require runtime data):** C1, C5, M5, M6, M7 — document as gated milestones, not prose.

---

## ERA V5 evaluator one-liner test

**After fix, the sentence:**  
> *IndiaOne maximizes deployable intelligence—useful work per rupee of inference—by treating the tokenizer as infrastructure under India's GPU, bandwidth, and code-switch constraints.*

**Memorable concept:** **Deployable Intelligence** (not "India-first model").

---

## Final funding posture

| Member | Reject? | Condition |
|--------|---------|-----------|
| Jeff Dean | No | Measure fertility before tranche 2 |
| Shazeer | No | 128k ablation on 10B sample published |
| Ilya | No | If §0 reads as hypothesis-driven |
| Nilekani | No | If deployment-first is spine, not data |
| VC | **Maybe** | $75M tranched; full $100M needs pilot |
| ERA V5 | No | If assignment Q1–Q4 still traceable in §3–§6, §9 |

**Verdict:** **Approve for evaluation submission** after §0 v2.3; **approve $100M** only with C1/C5 gates.
