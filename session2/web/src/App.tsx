import { useEffect, useState } from "react";
import { BPEEncoder, codePoints, scriptAttribution } from "./lib/bpe";
import { loadJson } from "./types";
import type { Stats, StrategyRow, OptTraceStep, RejectedMerge, SweepCurves } from "./types";
import {
  Hero,
  Scoreboard,
  FairnessRace,
  TokenEconomy,
  StrategyArena,
  RejectedGraveyard,
  ReproduceSection,
  Downloads,
  BudgetSimulator,
} from "./components/Sections";

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [strategies, setStrategies] = useState<StrategyRow[]>([]);
  const [trace, setTrace] = useState<OptTraceStep[]>([]);
  const [rejected, setRejected] = useState<RejectedMerge[]>([]);
  const [curves, setCurves] = useState<SweepCurves | null>(null);
  const [encoder, setEncoder] = useState<BPEEncoder | null>(null);
  const [playText, setPlayText] = useState("India भारत భారతదేశం ভারত");
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      loadJson<Stats>("/data/results/stats.json"),
      loadJson<StrategyRow[]>("/data/results/strategy_comparison.json"),
      loadJson<OptTraceStep[]>("/data/results/optimization_trace.json"),
      loadJson<RejectedMerge[]>("/data/results/rejected_merges.json"),
      loadJson<SweepCurves>("/data/results/vocab_sweep_curves.json"),
      BPEEncoder.load(),
    ])
      .then(([s, st, tr, rj, cu, enc]) => {
        setStats(s);
        setStrategies(st);
        setTrace(tr);
        setRejected(rj);
        setCurves(cu);
        setEncoder(enc);
      })
      .catch((e) => setError(String(e)));
  }, []);

  const tokens = encoder ? encoder.encode(playText) : [];
  const ids = encoder ? encoder.encodeIds(playText) : [];
  const vocabEntries = encoder?.getVocabEntries() ?? [];

  return (
    <div className="min-h-screen pb-20">
      {error && (
        <div className="bg-[var(--color-saffron)]/20 p-4 text-center text-sm">
          Artefacts not found — run the training pipeline first. ({error})
        </div>
      )}
      <Hero stats={stats} />
      <Scoreboard stats={stats} />
      <FairnessRace trace={trace} />
      <TokenEconomy allocation={stats?.vocab_allocation ?? {}} />
      <BudgetSimulator curves={curves} actualAlloc={stats?.vocab_allocation ?? {}} />

      <section className="mx-auto max-w-6xl px-4 py-10">
        <h2 className="text-2xl">Tokenizer Playground</h2>
        <textarea
          className="card mt-4 w-full font-mono text-sm"
          rows={4}
          value={playText}
          onChange={(e) => setPlayText(e.target.value)}
        />
        {encoder && (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="card">
              <div className="text-sm font-semibold">Tokens ({tokens.length})</div>
              <div className="mt-2 flex flex-wrap gap-1 font-mono text-xs">
                {tokens.map((t, i) => (
                  <button
                    key={i}
                    type="button"
                    className="rounded border border-[var(--color-indigo)]/20 bg-white/50 px-1 hover:bg-[var(--color-indigo)]/10"
                    onClick={() => setSelectedToken(t)}
                  >
                    {t.replace("</w>", "·")}
                  </button>
                ))}
              </div>
              <div className="mt-2 font-mono text-xs text-[var(--color-ink)]/60">IDs: {ids.join(", ")}</div>
            </div>
            <div className="card">
              <div className="text-sm font-semibold">Script attribution</div>
              <ul className="mt-2 space-y-1 font-mono text-xs">
                {tokens.map((t, i) => (
                  <li key={i}>{t.replace("</w>", "")} → {scriptAttribution(t)}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      <section className="mx-auto max-w-6xl px-4 py-10">
        <h2 className="text-2xl">Token Microscope</h2>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div className="card max-h-64 overflow-y-auto">
            <div className="text-sm font-semibold">Vocabulary ({vocabEntries.length})</div>
            <div className="mt-2 space-y-1 font-mono text-xs">
              {vocabEntries.slice(0, 200).map(({ token, id }) => (
                <button
                  key={id}
                  type="button"
                  className={`block w-full text-left hover:bg-white/50 ${selectedToken === token ? "bg-[var(--color-saffron)]/20" : ""}`}
                  onClick={() => setSelectedToken(token)}
                >
                  {id}: {token.replace("</w>", "·")}
                </button>
              ))}
            </div>
          </div>
          {selectedToken && (
            <div className="card font-mono text-sm">
              <div className="font-serif text-lg font-semibold">{selectedToken}</div>
              <dl className="mt-2 space-y-1">
                <div>ID: {encoder?.getVocabEntries().find((e) => e.token === selectedToken)?.id}</div>
                <div>Code points: {codePoints(selectedToken).join(" ")}</div>
                <div>Script: {scriptAttribution(selectedToken)}</div>
                <div>Code-point length: {selectedToken.length}</div>
                <div>Grapheme length: {[...selectedToken].length}</div>
              </dl>
            </div>
          )}
        </div>
      </section>

      <StrategyArena rows={strategies} winner={stats?.winning_strategy ?? ""} />
      <RejectedGraveyard items={rejected} />
      <ReproduceSection />
      <Downloads />

      <footer className="mx-auto max-w-6xl px-4 py-8 text-center text-sm text-[var(--color-ink)]/50">
        <p>Formula: X = tokens / word_units · Score = 1000 / (X_max − X_min)</p>
        <p className="mt-1">All headline metrics loaded from measured results/stats.json</p>
      </footer>
    </div>
  );
}
