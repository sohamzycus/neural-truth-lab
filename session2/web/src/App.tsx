import { useEffect, useState } from "react";
import { HfBpeEncoder } from "./lib/hf-encoder";
import { loadJson } from "./types";
import type { Stats, StrategyComparison, OptTraceStep, RejectedMerge, SweepCurves } from "./types";
import { ResubmissionHero, SectionInnovation, SectionLegacyNote } from "./components/ResubmissionHero";
import type { ResubmissionMetrics, ResubmissionExperiments, ResubmissionComparison } from "./types";
import { SiteNav, SectionExploreLab } from "./components/NarrativeSections";
import {
  SectionOptimizationTrace, SectionRejected, SectionGrapheme,
  SectionReproduce, SectionDownloads, BudgetSimulator,
} from "./components/StorySections";
import {
  SectionMovingBoundary, SectionOptimizerNextMove,
} from "./components/OptimizerStory";

const PRESETS = [
  "India भारत భారతదేశం ভারত",
  "India is a diverse country.",
  "भारत एक विविध देश है।",
  "భారతదేశం వైవిధ్యభరితమైన దేశం.",
  "ভারত একটি বৈচিত্র্যময় দেশ।",
  "see https://example.com/path for info",
  "भारत India বাংলা తెలుగు",
];

export default function App() {
  const [resubmission, setResubmission] = useState<ResubmissionMetrics | null>(null);
  const [experiments, setExperiments] = useState<ResubmissionExperiments | null>(null);
  const [comparison, setComparison] = useState<ResubmissionComparison | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [strategies, setStrategies] = useState<StrategyComparison | null>(null);
  const [trace, setTrace] = useState<OptTraceStep[]>([]);
  const [rejected, setRejected] = useState<RejectedMerge[]>([]);
  const [curves, setCurves] = useState<SweepCurves | null>(null);
  const [grapheme, setGrapheme] = useState<Record<string, { integrity_pct: number; split_clusters: number; total_graphemes: number }> | null>(null);
  const [encoder, setEncoder] = useState<HfBpeEncoder | null>(null);
  const [playText, setPlayText] = useState(PRESETS[0]);
  const [movingTrace, setMovingTrace] = useState<Array<Record<string, unknown>> | null>(null);
  const [roi, setRoi] = useState<{ candidates?: Array<Record<string, unknown>> } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<ResubmissionMetrics>("/data/results/resubmission_metrics.json"),
      loadJson<ResubmissionExperiments>("/data/results/resubmission_experiments.json").catch(() => null),
      loadJson<ResubmissionComparison>("/data/results/resubmission_comparison.json").catch(() => null),
      loadJson<Stats>("/data/results/stats.json").catch(() => null),
      loadJson<StrategyComparison | StrategyComparison["strategies"]>("/data/results/strategy_comparison.json").then((d) =>
        Array.isArray(d) ? { strategies: d as unknown as StrategyComparison["strategies"] } : d
      ).catch(() => null),
      loadJson<OptTraceStep[]>("/data/results/optimization_trace.json").catch(() => []),
      loadJson<RejectedMerge[]>("/data/results/rejected_merges.json").catch(() => []),
      loadJson<SweepCurves>("/data/results/vocab_sweep_curves.json").catch(() => null),
      loadJson<typeof grapheme>("/data/results/grapheme_stats.json").catch(() => null),
      loadJson<typeof movingTrace>("/data/results/moving_boundary_trace.json").catch(() => null),
      loadJson<typeof roi>("/data/results/score_roi_candidates.json").catch(() => null),
      HfBpeEncoder.load("/data/submission/tokenizer.json"),
    ])
      .then(([rs, ex, cmp, s, st, tr, rj, cu, gr, mt, roiData, enc]) => {
        setResubmission(rs);
        setExperiments(ex);
        setComparison(cmp);
        setStats(s);
        setStrategies(st);
        setTrace(tr);
        setRejected(rj);
        setCurves(cu);
        setGrapheme(gr);
        setMovingTrace(mt);
        setRoi(roiData);
        setEncoder(enc);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const tokens = encoder ? encoder.encodeTokens(playText) : [];
  const ids = encoder ? encoder.encodeIds(playText) : [];
  const alloc = stats?.vocab_attribution ?? stats?.vocab_allocation ?? {};

  return (
    <div className="min-h-screen pb-20">
      <SiteNav />
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm" role="alert">
          Failed to load application data. ({error})
        </div>
      )}

      <ResubmissionHero metrics={resubmission} experiments={experiments} comparison={comparison} />
      <SectionInnovation metrics={resubmission} experiments={experiments} />
      <SectionLegacyNote />

      <section className="mx-auto max-w-6xl px-4 py-14" id="playground">
        <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">Try the Hugging Face tokenizer</h2>
        <p className="mt-2 text-base text-[var(--color-ink)]/70">
          This playground loads the exact frozen <code className="text-xs">submission/tokenizer.json</code> winner
          — same pipeline as <code className="text-xs">encoder.py</code> (NFKC → word-ish normalize → whitespace →
          BPE).
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button key={p} type="button" className="btn text-xs" onClick={() => setPlayText(p)}>
              {p.slice(0, 28)}{p.length > 28 ? "…" : ""}
            </button>
          ))}
        </div>
        <textarea
          className="mt-4 w-full rounded border border-[var(--color-ink)]/15 bg-white/40 p-3 font-mono text-sm"
          rows={3}
          value={playText}
          onChange={(e) => setPlayText(e.target.value)}
          aria-label="Tokenizer input"
        />
        {encoder && (
          <div className="mt-4">
            <div className="text-sm font-semibold">Tokens ({tokens.length})</div>
            <div className="mt-2 flex flex-wrap gap-1 font-mono text-xs">
              {tokens.map((t, i) => (
                <span key={i} className="rounded border border-[var(--color-indigo)]/20 px-1">
                  {t}
                </span>
              ))}
            </div>
            <div className="mt-2 font-mono text-xs text-[var(--color-ink)]/60">IDs: {ids.join(", ")}</div>
          </div>
        )}
      </section>

      <SectionReproduce metrics={resubmission} />
      <SectionDownloads />

      <SectionExploreLab>
        <SectionOptimizerNextMove roi={roi as never} />
        <SectionMovingBoundary trace={movingTrace as never} sensitivity={null} />
        <SectionOptimizationTrace trace={trace} />
        <SectionRejected items={rejected} />
        <SectionGrapheme stats={grapheme} />
        <BudgetSimulator curves={curves} actualAlloc={alloc} />
      </SectionExploreLab>

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-[var(--color-ink)]/50">
        <p>
          Hugging Face BPE submission · <code>submission/metrics.json</code> ·{" "}
          <code>python evaluate_tokenizer.py</code>
        </p>
      </footer>
    </div>
  );
}
