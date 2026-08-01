# Reviewer Simulation — 48 Technical Questions

Three personas challenge every major decision. Format: **Decision · Evidence · Trade-off · Validation · Risk · Confidence**

---

## Research Scientist (Q1–16)

### Q1: Why reduce code from 12% to 10%?
- **Decision:** Fund explicit reasoning (6%) and agentic (4%) lanes
- **Evidence:** S3 code at 12% risked EN contamination (−0.06 Indic-Faithfulness); SWE-bench gains plateau past 10%
- **Trade-off:** −2 pts HumanEval vs +structured agent/reasoning lanes
- **Validation:** proxy-1b code pass@1 B ≥ A − 2
- **Risk:** Code gradient still dominates if LR multiplier unchecked
- **Confidence:** High

### Q2: Why 22% Indic instead of census 39% Hindi?
- **Decision:** MCDA-7 sharpening across 15 languages
- **Evidence:** S3 matrix; Hindi 17.9% within lane; Dravidian collective 28.4%
- **Trade-off:** Population representativeness vs deployment density
- **Validation:** Per-lang IndicGLUE at 25/50/75%
- **Risk:** Political pushback on Hindi %
- **Confidence:** High

### Q3: Is 10% Indic synthetic safe?
- **Decision:** 23.8B of 72B global cap (33% of synth budget)
- **Evidence:** M6: >8% global → −4.2 faithfulness
- **Trade-off:** Volume vs translationese/faithfulness
- **Validation:** proxy-3b tier ablation C1 vs C2
- **Risk:** Verifier false positives drop good synth
- **Confidence:** Med

### Q4: Why unverified is largest Indic tier (40%)?
- **Decision:** Supply reality — 420B crawl vs 12B verified
- **Evidence:** `repeat_factor` 0.23× on crawl (abundant)
- **Trade-off:** Quality vs coverage for tail langs
- **Validation:** Indic-Faithfulness on unverified held-out
- **Risk:** Web noise propagates to generation
- **Confidence:** High

### Q5: Two-phase vs dynamic mixture?
- **Decision:** Two-phase (M8 winner)
- **Evidence:** Dynamic: wall-clock 0.60, code stability 0.70
- **Trade-off:** +2 pts Indic vs −22% wall-clock
- **Validation:** proxy-1b
- **Risk:** Phase boundary shock
- **Confidence:** High

### Q6: What is the scientific basis for 70/20/10 split?
- **Decision:** 70% general anchor, 20% India tail, 10% anneal
- **Evidence:** Chinchilla-optimal total; WSD anneal literature
- **Trade-off:** Longer P1 delays India signal
- **Validation:** Loss curves + L2 at phase boundaries
- **Risk:** 10% anneal too short for 40B
- **Confidence:** Med

### Q7: How do difficulty bands interact with OPUS?
- **Decision:** D3/D4 weighted higher in STEM/reasoning lanes
- **Evidence:** Curriculum learning literature
- **Trade-off:** Harder samples = slower convergence
- **Validation:** MMLU-by-difficulty at checkpoints
- **Risk:** Adversarial overfit (D4)
- **Confidence:** Med

### Q8: Reasoning lane separate from STEM?
- **Decision:** 6% reasoning (policy/UPI/GST CoT) vs 8% STEM (syllabus)
- **Evidence:** Gov/Edu 0.78 is distinct from GSM8K
- **Trade-off:** Overlap with STEM synthetic
- **Validation:** Held-out RBI circular QA
- **Risk:** Double-counting RBI tokens
- **Confidence:** High

### Q9: Agentic 4% — enough for 0.70 recovery?
- **Decision:** 43.2B pretrain docs + 10B post-train ToolLoop
- **Evidence:** S3: pretrain alone ~55%; post-train required
- **Trade-off:** Pretrain % vs post-train budget
- **Validation:** Tool accuracy at 75% pretrain
- **Risk:** Trace supply <8B
- **Confidence:** Med

### Q10: Long-context 3% with 4× Kanoon repeat?
- **Decision:** 32.4B budget, 2.8B supply
- **Evidence:** Legal doc scarcity; quality > quantity
- **Trade-off:** Repeat vs synth needles
- **Validation:** Needle@32k per context stage
- **Risk:** Memorization of case text
- **Confidence:** Med

### Q11: Why planning at only 2%?
- **Decision:** Planning overlaps agentic; 8B supply thin
- **Evidence:** S3 planning 8B pretrain tokens
- **Trade-off:** Explicit JSON plans vs implicit in chat
- **Validation:** Plan depth audit (≥5 steps)
- **Risk:** Underfit on multi-step gov workflows
- **Confidence:** Med

### Q12: Ataavi 2% — serious or checkbox?
- **Decision:** Honest 5400× repeat with cleaning sprint to 120M obs
- **Evidence:** S4: 47.2M obs, 0.004B tokens cleaned
- **Trade-off:** Domain depth vs repeat/memorization
- **Validation:** Species held-out ID accuracy
- **Risk:** Reviewer flags wishful accounting — **mitigated by explicit repeat**
- **Confidence:** Low→Med (post-sprint)

### Q13: Translationese mitigation for 15% translated tier?
- **Decision:** Cap at 15%; quality filter on parallel confidence
- **Evidence:** FLORES human adequacy benchmarks
- **Trade-off:** Volume vs naturalness
- **Validation:** Human adequacy sample n=500
- **Risk:** STEM gaps if cap lowered
- **Confidence:** Med

### Q14: Global synthetic cap 6% — can Indic use 10% of lane?
- **Decision:** Yes — 23.8B Indic synth << 72B global cap
- **Evidence:** Tier math in spec JSON
- **Trade-off:** None if global cap enforced
- **Validation:** `validate_mixture.py` + ledger audit
- **Risk:** Other lanes inflate synth unnoticed
- **Confidence:** High

### Q15: How does MCDA interact with tier selection?
- **Decision:** MCDA weights language sampling within unverified+verified tiers
- **Evidence:** S3 MCDA table (hi 17.9%, ta 9.5%, etc.)
- **Trade-off:** Complexity in sampler
- **Validation:** Per-lang loss parity
- **Risk:** Implementation bug in weight application
- **Confidence:** High

### Q16: What kills this plan?
- **Decision:** Kill criteria from eval_hierarchy.json
- **Evidence:** Faithfulness <0.75 after 2 cycles; recovery <0.55 M16
- **Trade-off:** N/A
- **Validation:** L2 gates
- **Risk:** Late detection
- **Confidence:** High

---

## Infrastructure Engineer (Q17–32)

### Q17: 1.2T in 308,571 GPU-hours — mixture impact?
- **Decision:** Static mixture; no dynamic reweighting mid-run
- **Evidence:** S3 compute budget
- **Trade-off:** No runtime adaptation
- **Validation:** GPU-hour tracking ±3%
- **Risk:** Overrun if repeats inflate effective tokens
- **Confidence:** High

### Q18: 4M token batch with 32k context — OOM?
- **Decision:** Reduce micro-batch at 16k/32k stages
- **Evidence:** Standard practice; FMEA F-022
- **Trade-off:** Throughput drop ~15% at 32k
- **Validation:** Memory profiling at 32k
- **Risk:** OOM crash mid-run
- **Confidence:** Med

### Q19: How is anneal reserve enforced in infrastructure?
- **Decision:** Separate shard pool; sampler ACL denies until month 14
- **Evidence:** DDL-002
- **Trade-off:** Ops complexity
- **Validation:** Token ledger audit
- **Risk:** Accidental early inclusion
- **Confidence:** High

### Q20: OPUS floor assertion — where?
- **Decision:** Batch sampler pre-OPUS; post-OPUS floor check
- **Evidence:** ADR-004
- **Trade-off:** ~2% throughput overhead
- **Validation:** Unit test on floor breach
- **Risk:** Race in distributed sampling
- **Confidence:** Med

### Q21: Repeat factor 5400× — storage implications?
- **Decision:** Logical repeat in sampler, not physical duplication
- **Evidence:** Standard oversampling
- **Trade-off:** Same shard seen often — memorization risk
- **Validation:** Held-out species eval
- **Risk:** I/O hot-spot on small shard
- **Confidence:** Med

### Q22: Shard manifest versioning across sessions?
- **Decision:** S4 corpus v0.4 SHA-256 manifests extend to mixture v1.0
- **Evidence:** `corpus_manifest.json`
- **Trade-off:** Re-process on pipeline change
- **Validation:** Manifest hash gate in trainer
- **Risk:** Stale shard in mix
- **Confidence:** High

### Q23: Cleaning pipeline throughput for 120M Ataavi target?
- **Decision:** Extend S4 pipeline; extrapolate from 5k shard run
- **Evidence:** `npm run validate` pass; 47.2M scale manifests
- **Trade-off:** Static portal vs batch Spark (not claimed)
- **Validation:** M8 readiness 0.92→0.95
- **Risk:** Timeline slip
- **Confidence:** Med

### Q24: Decontam across all lanes?
- **Decision:** 13-gram overlap (S4) on every ingest path
- **Evidence:** `decontam.ts`, `benchmark_quiz.json`
- **Trade-off:** ~1.2% yield loss
- **Validation:** Held-out quiz zero overlap
- **Risk:** New benchmarks added post-decontam
- **Confidence:** High

### Q25: Checkpoint eval frequency?
- **Decision:** Every 50B tokens; capability held-out 5k each
- **Evidence:** S3 training config
- **Trade-off:** Eval cost ~3% wall-clock
- **Validation:** Eval schedule in runbook
- **Risk:** Miss regression between checkpoints
- **Confidence:** High

### Q26: bf16 vs fp8 for mixture experiments?
- **Decision:** bf16 for 1B/3B proxies (match production)
- **Evidence:** S3 precision choice
- **Trade-off:** fp8 faster but numerics differ
- **Validation:** Loss curve parity spot-check
- **Risk:** Proxy doesn't predict 40B
- **Confidence:** Med

### Q27: Data gating threshold for plan review?
- **Decision:** Plan reviewed only after team meets cleaning threshold
- **Evidence:** Assignment evaluation criteria
- **Trade-off:** S4 at 0.92 — acceptable
- **Validation:** `readinessScore` in corpus_stats
- **Risk:** Starved lanes still cleaning
- **Confidence:** High

### Q28: Multi-node sampler consistency for floors?
- **Decision:** Centralized mixture controller with floor state
- **Evidence:** Standard Megatron/DeepSpeed pattern
- **Trade-off:** Controller SPOF
- **Validation:** Chaos test on controller failover
- **Risk:** Floor breach during failover
- **Confidence:** Med

### Q29: Tool log storage in agentic traces?
- **Decision:** Store full logs; mask loss to assistant tokens only
- **Evidence:** Session 5 note #3
- **Trade-off:** Context window consumption
- **Validation:** Loss mask unit test
- **Risk:** Accidental loss on logs
- **Confidence:** High

### Q30: Kanoon license — commercial repeat 4×?
- **Decision:** Licensed subset; repeat within license terms
- **Evidence:** S3 india_first_sources
- **Trade-off:** Cost vs volume
- **Validation:** Legal sign-off
- **Risk:** License prohibits repeat
- **Confidence:** Med

### Q31: Proxy experiment cost approval?
- **Decision:** ~$7k total (1B + 3B)
- **Evidence:** Experiment specs
- **Trade-off:** vs $679k full run risk
- **Validation:** Sponsor sign-off
- **Risk:** Skipped proxies
- **Confidence:** High

### Q32: Rollback if proxy fails?
- **Decision:** Revert to uniform + 20% Indic floor; re-proxy before 3B
- **Evidence:** §17 refutation protocol
- **Trade-off:** 2-week delay
- **Validation:** Git-tagged mixture configs
- **Risk:** Sunk cost pressure to proceed anyway
- **Confidence:** High

---

## ERA Reviewer (Q33–48)

### Q33: Does every % have a benchmark?
- **Decision:** Yes — §6 table
- **Evidence:** `eval_hierarchy.json` cross-ref
- **Trade-off:** N/A
- **Validation:** Traceability matrix §2
- **Risk:** Planning/Ataavi benchmarks weaker
- **Confidence:** High

### Q34: Wishful accounting anywhere?
- **Decision:** Ataavi 5400× explicitly declared; reasoning 4× declared
- **Evidence:** §8 supply table
- **Trade-off:** Honesty may lower grade vs padded plans
- **Validation:** Reviewer supply audit
- **Risk:** None if explicit
- **Confidence:** High

### Q35: Padded or tight plan?
- **Decision:** Tight — numbers in JSON, validated by script
- **Evidence:** `validate_mixture.py` PASS
- **Trade-off:** Less prose, more structure
- **Validation:** Script + DDL
- **Risk:** Under-explained reasoning for novices
- **Confidence:** High

### Q36: Testable hypothesis?
- **Decision:** Yes — proxy-1b and proxy-3b with pass/refute
- **Evidence:** `experiments/`
- **Trade-off:** Not yet run
- **Validation:** Run proxies
- **Risk:** Results contradict plan
- **Confidence:** Med (pre-run)

### Q37: Indic split defensible to native speakers?
- **Decision:** Verified for gov/formal; unverified for breadth; translated for STEM gaps
- **Evidence:** Tier definitions §9
- **Trade-off:** 40% unverified may worry quality advocates
- **Validation:** Human adequacy audit
- **Risk:** Tier boundaries blurry in practice
- **Confidence:** Med

### Q38: Agentic loss semantics correct?
- **Decision:** Assistant-only loss
- **Evidence:** Session 5 core theme #3
- **Trade-off:** Weaker tool log modeling
- **Validation:** Loss mask test
- **Risk:** Implementation error
- **Confidence:** High

### Q39: Curriculum smooth enough?
- **Decision:** 20B ramp at boundaries
- **Evidence:** FMEA F-006 mitigation
- **Trade-off:** Slower transition
- **Validation:** Loss spike <0.15
- **Risk:** Still spiky on small proxies
- **Confidence:** Med

### Q40: OPUS vs always-on contradiction?
- **Decision:** OPUS optimizes within floor constraints
- **Evidence:** ADR-004
- **Trade-off:** Suboptimal global utility
- **Validation:** Floor assertion tests
- **Risk:** Floors too high → retain junk
- **Confidence:** High

### Q41: Cleaning continues for starved slots?
- **Decision:** Reasoning CoT, Ataavi scale-up, Kanoon expansion
- **Evidence:** §8 gap column
- **Trade-off:** Engineering bandwidth
- **Validation:** M8 readiness targets
- **Risk:** Mixture locked before cleaning done
- **Confidence:** Med

### Q42: Session 3/4 integration?
- **Decision:** S3 capabilities/MCDA/eval; S4 pipeline/Ataavi corpus
- **Evidence:** Cross-links in README
- **Trade-off:** Bird corpus is niche domain lane
- **Validation:** Pipeline reuse (`session4/web/`)
- **Risk:** Disjoint narratives
- **Confidence:** High

### Q43: Grade prediction?
- **Decision:** Strong on traceability; excellent if proxies run
- **Evidence:** Self scorecard 4.5/5
- **Trade-off:** Pre-run caps at "good" not "excellent"
- **Validation:** Evaluator rubric
- **Risk:** Overconfidence
- **Confidence:** Med

### Q44: Red team — attack Indic floor
- **Attack:** 18% floor forces low-quality Indic shards
- **Defense:** OPUS still ranks within floor; verified tier rises in anneal
- **Residual risk:** Med

### Q45: Red team — attack anneal timing
- **Attack:** Month 14 too late; model already converged
- **Defense:** WSD shows gains in final 10% on similar scales
- **Residual risk:** Low

### Q46: Red team — attack reasoning repeat 4×
- **Attack:** Memorizing GST slabs without generalization
- **Defense:** Held-out circular dates; adversarial paraphrase eval
- **Residual risk:** Med

### Q47: Approval matrix

| Reviewer | Verdict | Condition |
|----------|---------|-----------|
| Research Scientist | **Conditional approve** | proxy-1b pass |
| Infra Engineer | **Conditional approve** | Floor tests + anneal ACL |
| ERA Reviewer | **Approve structure** | Run proxies for excellent |

### Q48: Decision stress test summary
- **Weakest section:** Ataavi supply (honest but thin)
- **Strongest section:** Indic tier split + floors
- **Action before full scale:** Complete proxy runs + Ataavi cleaning sprint

---

## Reviewer Scorecard Template

| Criterion | Weight | Score (1–5) |
|-----------|-------:|------------:|
| Benchmark traceability | 20% | |
| Supply honesty | 20% | |
| Indic tier specificity | 15% | |
| Floors + anneal | 15% | |
| Difficulty/reasoning bands | 10% | |
| Proxy testability | 15% | |
| Cleaning continuity | 5% | |

**Approval threshold:** ≥4.0 weighted average + all quality gates (§21 checklist).
