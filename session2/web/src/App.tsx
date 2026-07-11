import { useEffect, useState } from "react";
import { BPEEncoder, codePoints, scriptAttribution, graphemeCount } from "./lib/bpe";
import { loadJson } from "./types";
import type { Stats, StrategyComparison, OptTraceStep, RejectedMerge, SweepCurves } from "./types";
import { HeroNarrative } from "./components/HeroNarrative";
import {
  SectionBottleneck, SectionOptimizerNextMove, SectionMovingBoundary, SectionTokenEconomyStory,
} from "./components/OptimizerStory";
import {
  SectionChallenge, SectionWhyFairness, SectionScoreboard, SectionPipeline,
  SectionStrategyArena, SectionFairnessRace,
  SectionRejected, SectionGrapheme, SectionReproduce, SectionDownloads, BudgetSimulator,
} from "./components/StorySections";

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
  const [sensitivity, setSensitivity] = useState<{ baseline_score?: number; improved?: boolean; best_track_a_score?: number } | null>(null);
  const [landscape, setLandscape] = useState<Record<string, unknown> | null>(null);
  const [roi, setRoi] = useState<{ candidates?: Array<Record<string, unknown>> } | null>(null);
  const [bottleneck, setBottleneck] = useState<Record<string, unknown> | null>(null);
  const [movingTrace, setMovingTrace] = useState<Array<Record<string, unknown>> | null>(null);
  const [headroom, setHeadroom] = useState<Record<string, unknown> | null>(null);
  const [proof, setProof] = useState<{
    claim?: string;
    mixed_script_highlight?: { input: string; tokens: string[]; token_count: number };
  } | null>(null);
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
      loadJson<typeof proof>("/data/results/one_tokenizer_proof.json").catch(() => null),
      loadJson<typeof sensitivity>("/data/results/objective_sensitivity.json").catch(() => null),
      loadJson<typeof landscape>("/data/results/score_landscape.json").catch(() => null),
      loadJson<typeof roi>("/data/results/score_roi_candidates.json").catch(() => null),
      loadJson<typeof bottleneck>("/data/results/bottleneck_word_analysis.json").catch(() => null),
      loadJson<typeof movingTrace>("/data/results/moving_boundary_trace.json").catch(() => null),
      loadJson<typeof headroom>("/data/results/english_headroom_analysis.json").catch(() => null),
      BPEEncoder.load(),
    ])
      .then(([s, st, tr, rj, cu, gr, pr, sens, land, roiData, bn, mt, hr, enc]) => {
        setStats(s);
        setStrategies(st);
        setTrace(tr);
        setRejected(rj);
        setCurves(cu);
        setGrapheme(gr);
        setProof(pr);
        setSensitivity(sens);
        setLandscape(land);
        setRoi(roiData);
        setBottleneck(bn);
        setMovingTrace(mt);
        setHeadroom(hr);
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
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm" role="alert">
          Artefacts not found — run <code>python scripts/verify.py</code> first. ({error})
        </div>
      )}

      <HeroNarrative stats={stats} proof={proof} sensitivity={sensitivity} />
      <SectionBottleneck stats={stats} landscape={landscape as never} bottleneck={bottleneck as never} />
      <SectionOptimizerNextMove roi={roi as never} />
      <SectionMovingBoundary trace={movingTrace as never} sensitivity={sensitivity} />
      <SectionReproduce stats={stats} />
      <SectionStrategyArena data={strategies} winner={stats?.winning_strategy ?? ""} stats={stats} />
      <SectionTokenEconomyStory stats={stats} headroom={headroom as never} />
      <SectionRejected items={rejected} />
      <div className="opacity-75">
        <SectionFairnessRace trace={trace} />
        <SectionPipeline />
        <SectionChallenge />
        <SectionWhyFairness />
        <SectionScoreboard stats={stats} />
      </div>

      <section className="mx-auto max-w-6xl px-4 py-12" id="playground">
        <h2 className="text-2xl font-bold">Tokenizer Playground</h2>
        <p className="text-sm text-[var(--color-ink)]/60">Same final tokenizer for all scripts — no language routing.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {PRESETS.map((p) => (
            <button key={p} type="button" className="btn text-xs" onClick={() => setPlayText(p)}>
              {p.slice(0, 24)}{p.length > 24 ? "…" : ""}
            </button>
          ))}
        </div>
        <textarea
          className="card mt-4 w-full font-mono text-sm"
          rows={3}
          value={playText}
          onChange={(e) => setPlayText(e.target.value)}
          aria-label="Tokenizer input"
        />
        {encoder && (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="card">
              <div className="text-sm font-semibold">Tokens ({tokens.length})</div>
              <div className="mt-2 flex flex-wrap gap-1 font-mono text-xs">
                {tokens.map((t, i) => (
                  <button key={i} type="button" className="rounded border border-[var(--color-indigo)]/20 bg-white/50 px-1 hover:bg-[var(--color-indigo)]/10" onClick={() => setSelectedToken(t)}>
                    {t.replace("</w>", "·")}
                  </button>
                ))}
              </div>
              <div className="mt-2 font-mono text-xs text-[var(--color-ink)]/60">IDs: {ids.join(", ")}</div>
            </div>
            <div className="card">
              <div className="text-sm font-semibold">Script attribution</div>
              <ul className="mt-2 max-h-40 overflow-y-auto space-y-1 font-mono text-xs">
                {tokens.map((t, i) => (
                  <li key={i}>{t.replace("</w>", "")} → {scriptAttribution(t)}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="microscope">
        <h2 className="text-2xl font-bold">Token Microscope</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="card max-h-64 overflow-y-auto">
            <div className="text-sm font-semibold">Vocabulary ({vocabEntries.length})</div>
            <div className="mt-2 space-y-1 font-mono text-xs">
              {vocabEntries.slice(0, 150).map(({ token, id }) => (
                <button key={id} type="button" className={`block w-full text-left hover:bg-white/50 ${selectedToken === token ? "bg-[var(--color-saffron)]/20" : ""}`} onClick={() => setSelectedToken(token)}>
                  {id}: {token.replace("</w>", "·")}
                </button>
              ))}
            </div>
          </div>
          {selectedToken && (
            <div className="card font-mono text-sm">
              <div className="font-serif text-lg font-semibold">{selectedToken}</div>
              <dl className="mt-2 space-y-1 text-xs">
                <div>ID: {encoder?.getVocabEntries().find((e) => e.token === selectedToken)?.id ?? "Not available"}</div>
                <div>Escaped: {JSON.stringify(selectedToken)}</div>
                <div>Code points: {codePoints(selectedToken).join(" ")}</div>
                <div>Script: {scriptAttribution(selectedToken)}</div>
                <div>Code-point length: {selectedToken.length}</div>
                <div>Grapheme length: {graphemeCount(selectedToken)}</div>
                <div>Merge ancestry: Not available</div>
                <div>Frequency: Not available</div>
              </dl>
            </div>
          )}
        </div>
      </section>

      <div className="opacity-80">
        <SectionGrapheme stats={grapheme} />
        <BudgetSimulator curves={curves} actualAlloc={alloc} />
      </div>
      <SectionDownloads />

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-xs text-[var(--color-ink)]/50">
        <p>Official metric: X = tokens ÷ word units · Verified self-score = 1000 ÷ (X<sub>max</sub> − X<sub>min</sub>)</p>
        <p className="mt-1">All headline metrics loaded from <code>results/stats.json</code> generated by <code>scripts/verify.py</code></p>
      </footer>
    </div>
  );
}
