import { useEffect, useState } from "react";
import { BPEEncoder, codePoints, scriptAttribution, graphemeCount } from "./lib/bpe";
import { loadJson } from "./types";
import type { Stats, StrategyComparison, OptTraceStep, RejectedMerge, SweepCurves } from "./types";
import { HeroNarrative } from "./components/HeroNarrative";
import {
  SiteNav, SectionExperiment, SectionWinner, SectionWhyWinner,
  SectionVocabularyEconomy, SectionExploreLab,
} from "./components/NarrativeSections";
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
];

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [strategies, setStrategies] = useState<StrategyComparison | null>(null);
  const [trace, setTrace] = useState<OptTraceStep[]>([]);
  const [rejected, setRejected] = useState<RejectedMerge[]>([]);
  const [curves, setCurves] = useState<SweepCurves | null>(null);
  const [grapheme, setGrapheme] = useState<Record<string, { integrity_pct: number; split_clusters: number; total_graphemes: number }> | null>(null);
  const [encoder, setEncoder] = useState<BPEEncoder | null>(null);
  const [playText, setPlayText] = useState(PRESETS[0]);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [movingTrace, setMovingTrace] = useState<Array<Record<string, unknown>> | null>(null);
  const [roi, setRoi] = useState<{ candidates?: Array<Record<string, unknown>> } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<Stats>("/data/results/stats.json"),
      loadJson<StrategyComparison | StrategyComparison["strategies"]>("/data/results/strategy_comparison.json").then((d) =>
        Array.isArray(d) ? { strategies: d as unknown as StrategyComparison["strategies"] } : d
      ),
      loadJson<OptTraceStep[]>("/data/results/optimization_trace.json"),
      loadJson<RejectedMerge[]>("/data/results/rejected_merges.json"),
      loadJson<SweepCurves>("/data/results/vocab_sweep_curves.json"),
      loadJson<typeof grapheme>("/data/results/grapheme_stats.json"),
      loadJson<typeof movingTrace>("/data/results/moving_boundary_trace.json").catch(() => null),
      loadJson<typeof roi>("/data/results/score_roi_candidates.json").catch(() => null),
      BPEEncoder.load(),
    ])
      .then(([s, st, tr, rj, cu, gr, mt, roiData, enc]) => {
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

  const tokens = encoder ? encoder.encode(playText) : [];
  const ids = encoder ? encoder.encodeIds(playText) : [];
  const vocabEntries = encoder?.getVocabEntries() ?? [];
  const alloc = stats?.vocab_attribution ?? stats?.vocab_allocation ?? {};

  return (
    <div className="min-h-screen pb-20">
      <SiteNav />
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm" role="alert">
          Run <code>python scripts/verify.py</code> first. ({error})
        </div>
      )}

      <HeroNarrative stats={stats} />
      <SectionExperiment data={strategies} />
      <SectionWinner stats={stats} />
      <SectionWhyWinner stats={stats} strategies={strategies} />
      <SectionVocabularyEconomy stats={stats} />

      <section className="mx-auto max-w-6xl px-4 py-14" id="playground">
        <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">Try the tokenizer</h2>
        <p className="mt-2 text-base text-[var(--color-ink)]/70">
          This playground uses the same authoritative tokenizer artefact submitted for scoring.
          {stats && (
            <span className="ml-1 font-mono text-xs text-[var(--color-ink)]/50">
              SHA-256 {stats.tokenizer_sha256.slice(0, 16)}…
            </span>
          )}
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
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <div>
              <div className="text-sm font-semibold">Tokens ({tokens.length})</div>
              <div className="mt-2 flex flex-wrap gap-1 font-mono text-xs">
                {tokens.map((t, i) => (
                  <button key={i} type="button" className="rounded border border-[var(--color-indigo)]/20 px-1 hover:bg-[var(--color-indigo)]/10" onClick={() => setSelectedToken(t)}>
                    {t.replace("</w>", "·")}
                  </button>
                ))}
              </div>
              <div className="mt-2 font-mono text-xs text-[var(--color-ink)]/60">IDs: {ids.join(", ")}</div>
            </div>
            <div>
              <div className="text-sm font-semibold">Script attribution (heuristic)</div>
              <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto font-mono text-xs">
                {tokens.map((t, i) => (
                  <li key={i}>{t.replace("</w>", "")} → {scriptAttribution(t)}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="vocabulary">
        <h2 className="text-2xl font-bold">Inspect the vocabulary</h2>
        <p className="mt-1 text-sm text-[var(--color-ink)]/60">
          Searchable slice of the submitted vocabulary ({vocabEntries.length} tokens). Download the full artefact below.
        </p>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="max-h-64 overflow-y-auto font-mono text-xs">
            {vocabEntries.slice(0, 200).map(({ token, id }) => (
              <button key={id} type="button" className={`block w-full text-left py-0.5 hover:bg-white/50 ${selectedToken === token ? "bg-[var(--color-saffron)]/20" : ""}`} onClick={() => setSelectedToken(token)}>
                {id}: {token.replace("</w>", "·")}
              </button>
            ))}
          </div>
          {selectedToken && (
            <div className="font-mono text-sm">
              <div className="text-lg font-semibold">{selectedToken}</div>
              <dl className="mt-2 space-y-1 text-xs">
                <div>ID: {encoder?.getVocabEntries().find((e) => e.token === selectedToken)?.id}</div>
                <div>Code points: {codePoints(selectedToken).join(" ")}</div>
                <div>Script: {scriptAttribution(selectedToken)}</div>
                <div>Graphemes: {graphemeCount(selectedToken)}</div>
              </dl>
            </div>
          )}
        </div>
      </section>

      <SectionReproduce stats={stats} />
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
        <p>Headline metrics from <code>results/stats.json</code> · <code>python scripts/verify.py</code></p>
      </footer>
    </div>
  );
}
