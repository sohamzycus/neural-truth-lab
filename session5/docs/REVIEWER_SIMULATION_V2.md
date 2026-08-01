# Reviewer Simulation V2 — Hostile Technical Review

Five personas · 10–15 questions each · Evidence → Risk → Confidence → Section

---

## Research Scientist (15 questions)

| # | Question | Evidence | Risk if wrong | Confidence | Section |
|---|----------|----------|---------------|------------|---------|
| RS-1 | Why 22% Indic not census 39% Hindi? | MCDA-7 deployment signals; S3 Dravidian collective 28.4%; proxy-1b +2.99pp indic | Political pushback; Hindi overfit | High | §6.1, §9 |
| RS-2 | Why 38% Web not 35% or 42%? | M8 two-phase needs EN-IN anchor; MMLU/TruthfulQA-IN gate | EN dominance hurts Indic | High | §6.1 |
| RS-3 | Why separate 6% reasoning from 8% STEM? | Gov/Edu 0.78 distinct from GSM8K; RBI/GST CoT supply | Double-counting RBI tokens | High | §6.1, §7 |
| RS-4 | Is 10% Indic synthetic safe? | 23.8B of 72B global cap; M6: >8% global → −4.2 faithfulness | Faithfulness drop | Med | §9, §28 |
| RS-5 | Why unverified largest Indic tier? | 420B crawl supply vs 12B verified; repeat 0.23× not 7× | Web noise in generation | Med | §8, §9 |
| RS-6 | Two-phase vs dynamic mixture? | M8: dynamic wall-clock 0.60; proxy-1b PASS | Phase boundary shock | High | §23, §17 |
| RS-7 | What refutes the mixture? | proxy-1b: indic delta <3pp; proxy-3b: needle <0.55 | Late detection at 40B | High | §17, §27 |
| RS-8 | 70/20/10 curriculum basis? | Chinchilla-optimal total; WSD anneal literature; M8 winner | 10% anneal too short | Med | §10, §25 |
| RS-9 | Difficulty band split rationale? | D3/D4 weighted in STEM/reasoning; curriculum literature | Adversarial overfit | Med | §11 |
| RS-10 | Planning at 2% — enough? | Overlaps agentic; 5B supply; plan depth audit gate | Underfit gov workflows | Med | §6, §26 |
| RS-11 | Ataavi 5400× repeat honest? | S4: 0.004B supply; cleaning sprint to 120M obs | Memorization | Low→Med | §8.1, §29 |
| RS-12 | Translationese at 15% translated? | Cap + FLORES adequacy sample n=500 | Unnatural register | Med | §9 |
| RS-13 | Global synth cap enforcement? | `validate_mixture.py` + ledger; Indic synth 33% of synth budget | Silent inflation | High | §28 |
| RS-14 | Kill criteria? | Faithfulness <0.75 ×2; recovery <0.55 M16 | Program pause | High | §18, DDL |
| RS-15 | What would you change with 2× verified Indic supply? | Shift 2pp unverified → verified; floor stays 18% | None — sensitivity §6.2 | Med | §6.2 |

---

## Infrastructure Engineer (12 questions)

| # | Question | Evidence | Risk | Confidence | Section |
|---|----------|----------|------|------------|---------|
| IE-1 | 1.2T in 308k GPU-hours — mixture impact? | Static mixture; no dynamic reweight mid-run | Overrun if repeats inflate | High | §5, DDL-001 |
| IE-2 | 32k context OOM? | Micro-batch reduction at 16k/32k; ~15% throughput drop | Mid-run crash | Med | §13, §29 |
| IE-3 | Anneal reserve ACL? | Separate shard pool; locked until month 14 | Accidental early spend | High | §15, §6.1 |
| IE-4 | OPUS floor assertion where? | Pre/post batch sampler; unit tests | Distributed race | Med | §16 |
| IE-5 | 5400× logical repeat I/O hot-spot? | Logical oversampling not physical duplication | Hot shard | Med | §8 |
| IE-6 | Manifest versioning? | S4 SHA-256; mixture v1.0 gate | Stale shard | High | §8 |
| IE-7 | Decontam on all lanes? | S4 13-gram on every ingest | New benchmark leakage | High | §18 |
| IE-8 | Checkpoint eval cadence? | Every 50B; 5k held-out per capability | Miss regression | High | ADR-002 |
| IE-9 | Multi-node floor consistency? | Centralized mixture controller | Failover breach | Med | §14 |
| IE-10 | Agentic loss mask on tool logs? | Assistant-only loss; unit test | Accidental log loss | High | §16 |
| IE-11 | Proxy cost vs full run risk? | ~$7k proxy vs $679k full | Skipped proxies | High | §17 |
| IE-12 | Rollback if proxy fails? | Uniform + 20% Indic floor; re-proxy | Sunk cost pressure | High | §17 |

---

## Training Engineer (12 questions)

| # | Question | Evidence | Risk | Confidence | Section |
|---|----------|----------|------|------------|---------|
| TE-1 | Why code 10% not 12%? | Room for reasoning+agentic; EN contamination at 16% | Code gradient dominance | High | §6.1, §24 |
| TE-2 | LR at phase boundaries? | 20B linear ramp; FMEA F-006 | Loss spike | Med | §10 |
| TE-3 | WSD anneal LR schedule? | Final 5% at 0.1× peak | Under-cool | Med | §15 |
| TE-4 | OPUS discard threshold 0.15? | Ghost-model utility calibration (§16) | Too aggressive discard | Med | §16, §27 |
| TE-5 | Context ramp 4k→32k timing? | P2 late + anneal; proxy-3b needle 0.777 | Recall cliff | High | §13, §17 |
| TE-6 | Batch composition floors? | Per-batch assert indic ≥18% effective | OPUS starvation | High | §14 |
| TE-7 | Synthetic memorization probe? | L11 leakage at 25/50/75% | Faithfulness drop | Med | §28 |
| TE-8 | Phase-2 India-heavy shock? | Gradual ramp not step | Instability | Med | §10, §25 |
| TE-9 | Code LR multiplier cap? | FMEA: NL plateau if code dominates | Indic regression | Med | §29 |
| TE-10 | Anneal mix composition? | 50% verified Indic / 30% HQ / 20% STEM-reasoning | Wrong cooldown mix | Med | §15 |
| TE-11 | ToolLoop post-train separate? | 10B traces not in 1.08T mix | Recovery stays 55% | High | §6, §7 |
| TE-12 | Repeat factor on reasoning 4×? | Verifier pipeline M10 dependency | Lane starvation | Med | §8, §8.1 |

---

## Benchmark Owner (11 questions)

| # | Question | Evidence | Risk | Confidence | Section |
|---|----------|----------|------|------------|---------|
| BO-1 | Every lane has offline benchmark? | §7 table; eval_hierarchy.json | Planning/Ataavi weaker | High | §7, §26 |
| BO-2 | IndicGLUE per-lang at checkpoints? | 25/50/75% pretrain eval | Tail lang miss | High | §17 |
| BO-3 | HumanEval+ vs SWE-bench tradeoff? | Code 10%; repos 42% subsource | LeetCode overfit if CP>2% | High | §6.1 |
| BO-4 | Needle@128k vs train 32k? | RoPE extension post-pretrain S3 | Deploy recall gap | Med | §13 |
| BO-5 | Gov/Edu 0.78 held-out? | RBI circular dates paraphrase | GST slab memorization | Med | §11, §12 |
| BO-6 | CS Index measurement? | BPO adherence + human A/B | ToS revocation on social | Med | §9 |
| BO-7 | Contamination protocol? | 13-gram S4; quiz held-out | Inflated offline | High | §18 |
| BO-8 | Proxy metrics vs real benchmarks? | Scheduler proxy ≠ IndicGLUE; 3B follow-up | False confidence | Med | §17, §28 |
| BO-9 | Species ID held-out for Ataavi? | Domain lane 2%; S4 decontam | Random domain QA | Low | §8 |
| BO-10 | L2 aggregate 0.78 gate? | eval_hierarchy ship_gate | Wrong ship decision | High | DDL |
| BO-11 | Benchmark-only ship rejected? | Indic-Faithfulness required | MMLU chasing | High | §4 |

---

## ERA Reviewer (14 questions)

| # | Question | Evidence | Risk | Confidence | Section |
|---|----------|----------|------|------------|---------|
| ER-1 | Wishful accounting anywhere? | Repeat factors declared §8; Ataavi 5400× explicit | Honesty penalty | High | §8 |
| ER-2 | Why 10% anneal not 5% or 15%? | Candidate table §6.1; WSD literature | Too short/long cooldown | Med | §6.1, §27 |
| ER-3 | Always-on 18% Indic floor? | OPUS starves tail; proxy-3b tail +4.52pp | Retains low-quality shards | Med | §14, §16 |
| ER-4 | Supply stress 50% shrink? | §8.1 recovery paths | Plan breaks silently | High | §8.1 |
| ER-5 | Uncertainty acknowledged? | §28 register | Overconfidence | High | §28 |
| ER-6 | Rejected alternatives documented? | §23 five+ designs | Looks arbitrary | High | §23 |
| ER-7 | Trade-offs explicit? | §24 matrix | Zero-sum hidden | High | §24 |
| ER-8 | Defense scores? | §30 table | Weak decisions exposed | High | §30 |
| ER-9 | Data gating before review? | S4 readiness 0.92 | Mixture ahead of cleaning | Med | §8 |
| ER-10 | Grade without GPU proxies? | Scheduler proxy PASS; 3B GPU pending | Good not excellent | Med | §17, §28 |
| ER-11 | Team can defend every %? | §6.1 evidence tables | Reviewer trap | High | §6.1 |
| ER-12 | What if wrong on Indic 22%? | §29 wrong-decision tree | Tail collapse | Med | §29 |
| ER-13 | Cleaning continues? | cleaning_manifest.json P0 lanes | Starved lanes | High | §8 |
| ER-14 | Final spec machine-readable? | mixture_spec.json + validate script | Drift | High | §22 |

---

## Red Team Summary

| Finding | Severity | Mitigation | Status |
|---------|----------|------------|--------|
| Ataavi 5400× repeat | Major | M8 cleaning sprint | Open |
| Reasoning 4× repeat | Major | CoT verifier M10 | Open |
| Scheduler proxy ≠ GPU 1B | Major | 3B GPU run queued | Open |
| Verified Indic 6.9× repeat | Minor | Gov pack sprint | In progress |

**Conditional approval:** Research Scientist + ERA Reviewer — **approve structure**; **require 3B GPU proxy** before full-scale commit.
