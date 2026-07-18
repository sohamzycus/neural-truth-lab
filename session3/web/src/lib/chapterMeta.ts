export type ChapterMeta = {
  insight: string;
  bullets: [string, string, string];
  takeaway: string;
};

export const CHAPTER_META: Record<string, ChapterMeta> = {
  "0": {
    insight: "Deployable Intelligence — optimize rupees per correct answer, not MMLU.",
    bullets: [
      "India's constraint is served tokens, not training data.",
      "Tokenizer is infrastructure; fine-tunes cannot fix fertility.",
      "Success = ₹/query, gov pilots, TCO — not leaderboard rank.",
    ],
    takeaway: "If §0 is clear, the rest of the report is evidence.",
  },
  "1": {
    insight: "Ten capabilities with SLOs — nothing enters the corpus without a contract.",
    bullets: [
      "Four joint constraints: multilingual, India Stack, agentic, frugal inference.",
      "40B India-first beats fine-tune on differentiation, not parameter count.",
      "Every capability maps to eval in §9.",
    ],
    takeaway: "L1: capabilities define data.",
  },
  "2": {
    insight: "40B dense GQA is the Pareto point on 2×L40S — not MoE, not 70B.",
    bullets: [
      "MoE adds routing latency; 70B breaks SME TCO.",
      "M12 weighted score 0.83 vs 0.77 MoE.",
      "128k context via RoPE serves long_context capability.",
    ],
    takeaway: "Architecture follows deployment envelope first.",
  },
  "3": {
    insight: "Data mix is derived from capabilities via MCDA-7 — not census Hindi.",
    bullets: [
      "Hindi 17.9% MCDA vs 39.2% population — anti-crawl-noise.",
      "1.2T = 82/12/4/6 NL/code/math/synthetic.",
      "India Stack flows through indian_reasoning capability.",
    ],
    takeaway: "Assignment Q1 answered as capability → signal → corpus.",
  },
  "4": {
    insight: "16-stage DAG trades 22.2% yield for 0.82 faithfulness — ship timeline.",
    bullets: [
      "4.5× over-collection (~5.4T raw) funds strict cleaning.",
      "L14 OCR and L11 leakage are India-critical stages.",
      "Code path includes L12 compile gate.",
    ],
    takeaway: "Assignment Q2: industrial cleaning, not single-pass filter.",
  },
  "5": {
    insight: "128k wins deploy composite 0.746 — beats 192k/256k on economics.",
    bullets: [
      "Unigram+BPE hybrid for Indic conjunct stability.",
      "Vocab derived from script exposure, not convention.",
      "1.22 GB embedding fits 2×L40S budget.",
    ],
    takeaway: "L4: tokenizer is permanent infrastructure.",
  },
  "6": {
    insight: "21% fertility reduction ≈ $13M/yr — often exceeds pretrain cost.",
    bullets: [
      "1.46 → 1.14 avg Indic fertility vs generic.",
      "Blended 8B/40B router: ~$19M Year-2 TCO.",
      "Longer context compounds fertility savings.",
    ],
    takeaway: "L3: inference tokens are deployment currency.",
  },
  "7": {
    insight: "Two-phase curriculum: 70% general anchor → 30% India-heavy tail.",
    bullets: [
      "$679k per full run · 308,571 H100-hr.",
      "Synthetic capped at 6%; >8% hurts faithfulness.",
      "Checkpoint eval every 50B tokens.",
    ],
    takeaway: "Training schedule serves capability convergence, not uniform mixing.",
  },
  "8": {
    insight: "DPO primary; RLHF safety-only — recovery 55% → 70% target.",
    bullets: [
      "$12M alignment · ToolLoop with 30% failure injection.",
      "11 agent sub-capabilities with dedicated training signal.",
      "Hinglish SFT non-negotiable for CS gate.",
    ],
    takeaway: "L5: unmeasured recovery is uncommitted agentics.",
  },
  "9": {
    insight: "Pyramid eval: L1–L3 gate release; L4 benchmarks monitor only.",
    bullets: [
      "Five scorecards with explicit thresholds.",
      "10 capabilities → offline → real-world → business KPI.",
      "MMLU does not gate ship.",
    ],
    takeaway: "Assignment Q3: objectives, not benchmark lists.",
  },
  "10": {
    insight: "INT4 default · FP8 gov · 80/20 8B/40B blend on Mumbai/Chennai edge.",
    bullets: [
      "p99 < 800ms · 2× L40S per replica.",
      "$5M pilot budget across gov, BPO, SME, ed-tech.",
      "Fertility reduces bytes on low-bandwidth paths.",
    ],
    takeaway: "Deployment is the product; the model is the engine.",
  },
  "11": {
    insight: "$100M / 18mo with kill criteria — no sunk-cost escalation.",
    bullets: [
      "3.77M GPU-hours · contingency 10%.",
      "Pause on faithfulness <0.75; terminate agent <0.55.",
      "Monthly burn $5.56M target.",
    ],
    takeaway: "Funding follows gates, not hope.",
  },
  A: {
    insight: "M1–M12 matrices trace every locked decision to evidence.",
    bullets: [
      "128k vocab · MCDA-7 · 16-stage clean · DPO alignment.",
      "All numbers from derive_all.py.",
      "Cross-links §2–§10.",
    ],
    takeaway: "Traceability without re-reading the full report.",
  },
  C: {
    insight: "We are not optimizing Benchmark Intelligence.",
    bullets: [
      "We optimize Deployable Intelligence.",
      "Production flywheel closes the loop to V2.",
      "Success = useful work per rupee of inference.",
    ],
    takeaway: "We are not optimizing Benchmark Intelligence. We are optimizing Deployable Intelligence.",
  },
};
