import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import type { Stats, StrategyRow, OptTraceStep, RejectedMerge, SweepCurves } from "../types";

const LANG_COLORS: Record<string, string> = {
  en: "#2c3e6b",
  hi: "#c45c26",
  te: "#2d5a3d",
  bn: "#6b3a5c",
};

export function Hero({ stats }: { stats: Stats | null }) {
  if (!stats) {
    return (
      <header className="relative overflow-hidden py-16 text-center">
        <p className="text-lg text-[var(--color-ink)]/60">Loading measured results…</p>
      </header>
    );
  }
  return (
    <header className="relative overflow-hidden py-16 text-center">
      <span className="script-watermark left-4 top-4">भारत</span>
      <span className="script-watermark right-8 bottom-4">భారత</span>
      <span className="script-watermark left-1/3 bottom-8">ভারত</span>
      <p className="text-sm uppercase tracking-[0.3em] text-[var(--color-saffron)]">Measured · Verified</p>
      <h1 className="mt-2 text-5xl md:text-6xl">SamaBPE</h1>
      <p className="mt-3 text-xl italic text-[var(--color-ink)]/80">
        One vocabulary. Four scripts. One objective: equality.
      </p>
      <div className="mx-auto mt-8 grid max-w-4xl grid-cols-2 gap-4 px-4 md:grid-cols-5">
        {[
          ["Vocabulary", stats.vocabulary_size.toLocaleString()],
          ["Languages", "4"],
          ["Self-Score", stats.score.toFixed(2)],
          ["Max−Min Gap", stats.max_min_gap.toFixed(4)],
          ["EN ≤ 1.2", stats.english_constraint.pass ? "PASS" : "FAIL"],
        ].map(([k, v]) => (
          <div key={k} className="card text-center">
            <div className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">{k}</div>
            <div className="mt-1 font-mono text-lg font-semibold">{v}</div>
          </div>
        ))}
      </div>
    </header>
  );
}

export function Scoreboard({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Scoreboard</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.languages.map((l) => (
          <div key={l.lang} className="card relative">
            <div
              className="absolute left-0 top-0 h-1 w-full rounded-t-lg"
              style={{ background: LANG_COLORS[l.lang] }}
            />
            <h3 className="text-xl">{l.label}</h3>
            <dl className="mt-3 space-y-1 font-mono text-sm">
              <div className="flex justify-between"><dt>Characters</dt><dd>{l.characters.toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt>Word units</dt><dd>{l.word_units.toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt>Tokens</dt><dd>{l.tokens.toLocaleString()}</dd></div>
              <div className="flex justify-between font-semibold"><dt>Fertility X</dt><dd>{l.fertility.toFixed(4)}</dd></div>
              <div className="flex justify-between"><dt>Rank</dt><dd>#{l.rank}</dd></div>
            </dl>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FairnessRace({ trace }: { trace: OptTraceStep[] }) {
  const data = trace.map((t) => ({
    step: t.step,
    en: t.fertilities.en,
    hi: t.fertilities.hi,
    te: t.fertilities.te,
    bn: t.fertilities.bn,
    gap: t.max_min_gap,
  }));
  if (!data.length) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Fairness Race</h2>
      <p className="mt-1 text-sm text-[var(--color-ink)]/60">Optimization trace — measured fertilities per iteration</p>
      <div className="card mt-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="step" />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Legend />
            {(["en", "hi", "te", "bn"] as const).map((lang) => (
              <Line key={lang} type="monotone" dataKey={lang} stroke={LANG_COLORS[lang]} dot={false} strokeWidth={2} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function TokenEconomy({ allocation }: { allocation: Record<string, number> }) {
  const data = Object.entries(allocation).map(([name, value]) => ({ name, value }));
  const colors = ["#2c3e6b", "#c45c26", "#2d5a3d", "#6b3a5c", "#8b7355"];
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">10K Token Economy</h2>
      <div className="card mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" width={80} />
            <Tooltip />
            <Bar dataKey="value">
              {data.map((_, i) => (
                <Cell key={i} fill={colors[i % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function StrategyArena({ rows, winner }: { rows: StrategyRow[]; winner: string }) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Strategy Arena</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-[var(--color-ink)]/20 text-left">
              {["Strategy", "Vocab", "EN", "HI", "TE", "BN", "Gap", "Score", "EN≤1.2"].map((h) => (
                <th key={h} className="p-2 font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr
                key={r.strategy}
                className={`border-b border-[var(--color-ink)]/10 ${r.strategy === winner ? "bg-[var(--color-saffron)]/10 font-semibold" : ""}`}
              >
                <td className="p-2 font-mono">{r.strategy}</td>
                <td className="p-2">{r.vocabulary_size}</td>
                <td className="p-2">{r.en_fertility.toFixed(3)}</td>
                <td className="p-2">{r.hi_fertility.toFixed(3)}</td>
                <td className="p-2">{r.te_fertility.toFixed(3)}</td>
                <td className="p-2">{r.bn_fertility.toFixed(3)}</td>
                <td className="p-2">{r.max_min_gap.toFixed(4)}</td>
                <td className="p-2">{r.score.toFixed(2)}</td>
                <td className="p-2">{r.english_pass ? "✓" : "✗"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function RejectedGraveyard({ items }: { items: RejectedMerge[] }) {
  if (!items.length) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Rejected Merges Graveyard</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {items.slice(0, 20).map((r, i) => (
          <div key={i} className="card font-mono text-xs">
            <div className="text-base font-serif font-semibold">{r.candidate}</div>
            <div>freq: {r.frequency} · {r.language}</div>
            <div>score {r.old_score.toFixed(1)} → {r.predicted_score.toFixed(1)}</div>
            <div className="mt-1 text-[var(--color-saffron)]">{r.reason}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function ReproduceSection() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Reproduce My Score</h2>
      <pre className="card mt-4 overflow-x-auto font-mono text-sm">
{`cd session2
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/fetch_corpora.py
python scripts/train.py
python scripts/verify.py`}
      </pre>
    </section>
  );
}

export function Downloads() {
  const files = [
    "results/tokenizer.json",
    "results/vocab.json",
    "vocab.txt",
    "merges.txt",
    "results/stats.json",
    "results/optimization_trace.json",
    "results/vocab_allocation.json",
    "results/grapheme_stats.json",
    "results/rejected_merges.json",
    "results/manifest.sha256.json",
    "corpora/frozen/en_india.txt",
    "corpora/frozen/hi_india.txt",
    "corpora/frozen/te_india.txt",
    "corpora/frozen/bn_india.txt",
  ];
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Downloads</h2>
      <div className="mt-4 flex flex-wrap gap-2">
        {files.map((f) => (
          <a key={f} className="btn" href={`/data/${f}`} download>
            {f.split("/").pop()}
          </a>
        ))}
      </div>
    </section>
  );
}

export function BudgetSimulator({
  curves,
  actualAlloc,
}: {
  curves: SweepCurves | null;
  actualAlloc: Record<string, number>;
}) {
  if (!curves) return null;
  const enCurve = curves.per_language.en ?? [];
  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h2 className="text-2xl">Budget Simulator</h2>
      <p className="text-sm text-[var(--color-ink)]/60">
        Curves are measured from vocabulary sweeps. Sliders show <em>predicted</em> estimates.
      </p>
      <div className="card mt-4">
        <p className="font-mono text-sm">Optimizer allocation: {JSON.stringify(actualAlloc)}</p>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={enCurve}>
              <XAxis dataKey="vocab_size" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="fertility" stroke={LANG_COLORS.en} name="EN fertility (measured sweep)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
