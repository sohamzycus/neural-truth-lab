# Committee Review — IndiaOne-40B

**Committee:** Jeff Dean (systems) · Noam Shazeer (foundation models) · Nandan Nilekani (India digital) · Dario Amodei (alignment/scaling) · Skeptical VC ($100M)  
**Live:** https://india-40b-erav5.netlify.app/  
**Verdict:** **CONDITIONAL FUND — $75M / 18mo** with milestone gates; not full $100M until tokenizer economics are measured on production traffic and one gov pilot ships.

---

## Task 1 — What is this report really saying?

### 1. One sentence

**IndiaOne exists because India's AI stack fails at inference economics and script-aware tokenization—not at pretraining scale—and this program optimizes ₹/query and deployable capability before leaderboard rank.**

### 2. What the authors believe

They believe foundation models are **infrastructure**, not research trophies: the binding constraint for India is not "another 40B" but **tokens per rupee on constrained GPUs**, and that constraint should reverse-engineer vocabulary, data mix, eval gates, and architecture. They believe **capabilities must be contracted before corpora are bought**, and that **Gemma/Llama-class models cannot be fine-tuned into this optimum** because the tokenizer tax is permanent.

### 3. Differentiation vs incumbents

| Model | What it optimizes | IndiaOne claim |
|-------|-------------------|----------------|
| **Gemma** | Google-scale EN + safety; efficient small models | Gemma's vocab is not script-economic; fine-tune doesn't fix fertility |
| **Llama** | Global open-weight; EN MMLU | 1.46 Indic fertility → SME TCO failure |
| **Qwen** | Multilingual breadth + code | Deployment story is China-cloud centric; no India TCO/router |
| **DeepSeek** | Cost-efficient training + code | No India digital stack (UPI/GST/ONDC) or frugal edge deploy |
| **Mistral** | EU efficiency + MoE option | MoE rejected for Indic routing latency; no MCDA anti-population |

**Unique thesis (if true):** *Deployable intelligence* — optimize the **inference stack** (tokenizer → fertility → INT4 → 8B/40B blend) as the moat, not parameter count.

### 4. If differentiation disappeared, would the report still make sense?

**No.** Remove fertility/TCO and MCDA-7 anti-population weighting and this becomes a competent but generic "multilingual 40B with Indian data" proposal—indistinguishable from a Qwen fine-tune spec. §3's UPI/GST tables alone do not justify $100M; §6's $64M→$19M story does.

### 5. What will an evaluator remember in one week?

**Most likely:** *"21% tokenizer savings, $64M to $19M TCO, 128k vocab."*  
**Risk:** They remember **numbers**, not **philosophy**.  
**Why not more:** §0 lists decisions before establishing inevitability; India-first reads as **corpus inventory** (Hindi, NCERT, RBI) not **structural reality** (mobile, bandwidth, SME, code-switch as default cognition).

---

## Task 2 — HOW before WHY (redesign candidates)

| Location | Offense | Fix |
|----------|---------|-----|
| §0 D4, P2 | States 128k before economic law | Lead: *deployment economics → tokenizer is infrastructure* → then 128k |
| §2.5 | Hyperparameter table before constraint story | Open with 2×L40S as hard constraint, not sponsor target |
| §3.2–3.3 | MCDA table before *why not population* | One sentence: population weighting optimizes crawl noise, not deployment demand |
| §4.5 | Stage list before *why 22% yield is acceptable* | Lead: ship timeline vs faithfulness gate |
| §5.1–5.3 | "What tokenizer" then Pareto | §6 causal chain should open §5 |
| §7.5 | Compute table before *why two-phase* | Phase 2 exists because India tail langs underfit under uniform sampling |
| §8.2 | Alignment method table before agent failure rate | Lead: 55% recovery is the problem |
| §9.5 | Scorecard gates before pyramid rationale | L4 is monitoring because leaderboard optimization is explicitly rejected |
| §10.2 | Quantization table before SME constraint | Mobile/bandwidth belongs in problem statement |
| §11.2 | Budget table before kill criteria philosophy | Contingency exists because faithfulness kills are real |

**Pattern:** Strong engineering template (Problem → Options → Matrix → Chosen) often **hides** the philosophical WHY inside tables. Evaluators skim tables; they remember the first sentence of each chapter.

---

## Task 3 — Five Engineering Laws (should govern entire report)

| Law | Meaning | Chapters it explains |
|-----|---------|---------------------|
| **L1 — Capabilities before corpus** | No token budget without SLO | §1, §3, §9 |
| **L2 — Deployment before leaderboard** | Ship gates > MMLU | §9, §0, §11 |
| **L3 — Inference economics dominate training** | Fertility/TCO reverse-engineer vocab, quant, blend | §5, §6, §10 |
| **L4 — Tokenizer is infrastructure** | Vocab choice is permanent tax; not an NLP detail | §5, §6, §2 |
| **L5 — Every capability needs an observable SLO** | If you can't measure it, you didn't commit | §1, §8, §9 |

**Gap:** Laws are implicit; evaluator must infer them. §0 "Design Principles" are close but read as **checklist**, not **physics**.

---

## Task 4 — India-first: implementation vs philosophy

**Current (implementation):** Hindi %, GST, UPI, NCERT, Kanoon, Hinglish social.  
**Missing (philosophy):** India is not language-first—it is:

| Reality | Should drive | Currently drives |
|---------|--------------|------------------|
| **Deployment-first** (2×L40S, edge) | Architecture, quant, router | §2, §10 — good but late |
| **Mobile-first** | 8B tier, bytes/query | Mentioned §10, not spine |
| **Bandwidth-constrained** | Fertility, blended router | §6 — strongest chapter |
| **GPU-constrained** | INT4 default, not FP16 | §10 — good |
| **Code-switching as default** | Tokenizer + eval + post-train | Scattered |
| **SME-dominated** | ₹/query success metric | §0 mission — underdeveloped |
| **Gov digitization at scale** | Faithfulness gates, FP8 tier | §9 — good |

**Nilekani's line:** *"You built a corpus map for India Stack. You did not yet argue India Stack is why the model architecture cannot be imported."*

---

## Task 5 — Challenge every decision (devil's advocate)

| Decision | Why not opposite? | Report defense | Gap |
|----------|-------------------|----------------|-----|
| 128k not 256k | Lower fertility | Embedding blocks 2×L40S; composite 0.746 | **No measured fertility on target corpus** |
| 128k not 160k/192k | Marginal fertility gain | +0.31GB for −0.02 fertility | Adequate |
| 40B dense not MoE | Active-param efficiency | Routing latency 40–80ms; uneven Indic experts | Adequate |
| 40B not 70B | TCO | 4×L40S, $98M TCO | Adequate |
| DPO not RLHF-primary | Cost/speed | 2.1× cost | Adequate |
| 12% not 20% code | EN contamination | Faithfulness −0.06 | Adequate |
| MCDA not population | Hindi web noise | 39.2% vs 17.9% | **Strong—memorable** |
| 128k context not 1M | Long legal docs | Kanoon chunks; fertility compounds | Weak for judiciary use case |
| INT4 not FP16 | SME viability | $4.90/M vs $1.85 blended | Adequate |
| 6% synthetic not 10% | Faithfulness −4.2 | Ablation cited | Unverified externally |

**Weakest defenses:** fertility numbers (derived, not measured); agent 70% recovery (ambitious without pilot data); DeepSeek-class cost pressure ("tokenizer moat" may be insufficient if competitor ships India-tuned 8B at $0.10/M).

---

## Task 6–9 — Chapter audit (Why / What / Why not / Risk / Validation / Business / Deploy)

| § | Why | What | Why not | Risk | Validation | Business | Deploy | Grade |
|---|-----|------|---------|------|------------|----------|--------|-------|
| 0 | Partial | Strong | Strong | Strong | Strong | Weak | Medium | B+ |
| 1 | Strong | Strong | Strong | Strong | Medium | Weak | Medium | B+ |
| 2 | Medium | Strong | Strong | Strong | Medium | Weak | Strong | B |
| 3 | Strong | Strong | Strong | Strong | Strong | Medium | Weak | A- |
| 4 | Medium | Strong | Strong | Strong | Strong | Weak | Weak | B |
| 5 | **Weak** | Strong | Strong | Medium | Medium | Strong | Strong | B |
| 6 | **Strong** | Strong | Strong | Strong | Strong | **Strong** | **Strong** | **A** |
| 7 | Medium | Strong | Strong | Strong | Medium | Weak | Weak | B |
| 8 | Medium | Strong | Strong | Strong | Strong | Medium | Strong | B+ |
| 9 | Strong | Strong | Strong | Strong | Strong | Strong | Strong | A |
| 10 | Strong | Strong | Strong | Strong | Strong | **Strong** | **Strong** | A |
| 11 | Strong | Strong | Strong | **Strong** | Strong | Strong | Strong | A- |

**Systemic gap:** Business impact appears in §9/§10 but not wired back to §1–§4 openings.

---

## Task 7–8 — First three pages & executive (committee prescription)

**Page 1 — Vision:** India doesn't need the best model on MMLU; it needs the cheapest **correct** token on a Mumbai GPU.  
**Page 2 — Why IndiaOne:** Incumbents optimize training; India optimizes **serving**.  
**Page 3 — Five Laws:** L1–L5 above; every later chapter cites a law ID.

**Executive must answer only:**
1. **Problem:** Indic inference costs 21–45% more per query on imported tokenizers → SME and gov scale blocked.  
2. **Why not existing:** Fine-tuning cannot change vocab; leaderboard models optimize EN.  
3. **Philosophy:** Deployable intelligence — L1–L5.  
4. **Success:** ₹/query, gov pilot ≥0.78, TCO savings ≥10%, not MMLU rank.

---

## Task 10 — Emotional inevitability

**What works:** §6 causal chain; MCDA anti-population; kill criteria; pyramid eval.  
**What blocks inevitability:** Template repetition; §0 reads like a **dashboard** not a **manifesto**; Gemma/Llama contrast is one line.

**Target feeling:** *"Of course you can't fine-tune Llama for this—tokenizer is infrastructure."*  
**Current feeling:** *"These engineers thought hard and built good matrices."*

---

## Final brutal review — reasons to reject

| Rejector | Kill shot |
|----------|-----------|
| **Jeff Dean** | Fertility and yield numbers are modeled, not measured at scale |
| **Shazeer** | 40B dense in 2026 is not differentiated; 8B distill + router may suffice |
| **Nilekani** | India story is datasets, not digital-public-infrastructure philosophy |
| **Dario** | $12M alignment on 40B is thin; safety RLHF slice feels checkbox |
| **VC** | $100M for 21% TCO savings requires belief in 30M queries/day—unproven |

**What would flip the VC to full yes:**
1. Measured fertility A/B on 10k production-shaped prompts (not derived JSON).  
2. One signed gov/SME pilot letter before tranche 2.  
3. §0 rewritten so thesis is unforgettable in 30 seconds.

---

## Funding decision

| Member | Vote | Amount |
|--------|------|--------|
| Jeff Dean | Yes, gated | $80M |
| Shazeer | Yes, smaller | $60M |
| Nilekani | Yes, if philosophy sharpened | $75M |
| Dario | Conditional | $70M |
| VC | **Conditional** | **$75M** |

**Committee consensus:** **FUND at $75M** with tranches: $40M pretrain · $20M align/eval · $15M deploy pilots. Hold $25M until Month-12 gates (faithfulness ≥0.78, fertility A/B confirmed, one pilot live).

**Success criterion met?** Partially. Technical maturity is high; **memorable philosophy** is not yet at the level of the engineering.

---

*Review only. Surgical §0 edits applied separately in REPORT.md v2.2.*
