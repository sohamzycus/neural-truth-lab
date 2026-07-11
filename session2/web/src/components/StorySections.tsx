import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell,
} from "recharts";
import type { Stats, StrategyComparison, OptTraceStep, RejectedMerge, SweepCurves } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_COLORS: Record<string, string> = {
  en: "#2c3e6b", hi: "#c45c26", te: "#2d5a3d", bn: "#6b3a5c",
};

export function SectionChallenge() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="challenge">
      <h2 className="text-2xl font-bold">The Challenge</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="card">
          <ul className="space-y-2 text-sm">
            <li>One vocabulary · 10,000 token slots · 4 languages</li>
            <li>English must be ≤ 1.20 tokens per word unit</li>
            <li>Goal: minimize max(X) − min(X)</li>
          </ul>
        </div>
        <div className="card font-mono text-sm">
          <div>X<sub>language</sub> = encoded tokens ÷ word units</div>
          <div className="mt-2">Score = 1000 ÷ (X<sub>max</sub> − X<sub>min</sub>)</div>
          <p className="mt-3 font-serif text-[var(--color-ink)]/70">
            The closer the four ratios are, the higher the score.
          </p>
        </div>
      </div>
    </section>
  );
}

export function SectionWhyFairness() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">Why Token Fairness Matters</h2>
      <div className="card mt-4 border-dashed">
        <p className="text-xs uppercase tracking-wider text-[var(--color-saffron)]">Illustrative example — not a benchmark</p>
        <div className="mt-3 grid gap-4 md:grid-cols-2 font-mono text-sm">
          <div>Language A: 10 words → 12 tokens (X = 1.2)</div>
          <div>Language B: 10 words → 24 tokens (X = 2.4)</div>
        </div>
        <p className="mt-3 text-sm text-[var(--color-ink)]/70">
          Roughly 2× token processing cost and half the equivalent content in a fixed context window.
        </p>
      </div>
    </section>
  );
}

export function SectionScoreboard({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="scoreboard">
      <h2 className="text-2xl font-bold">The Verified Scoreboard</h2>
      <p className="mt-1 text-sm text-[var(--color-ink)]/60">
        <span className="rounded bg-[var(--color-leaf)]/15 px-1.5 py-0.5 text-xs font-medium">VERIFIED</span>
        {" "}from independent verification pipeline
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.languages.map((l) => (
          <div key={l.lang} className="card" style={{ borderTop: `3px solid ${LANG_COLORS[l.lang]}` }}>
            <h3 className="text-lg">{LANG_DISPLAY[l.lang]?.native ?? l.label}</h3>
            <dl className="mt-2 space-y-1 font-mono text-xs">
              <div className="flex justify-between"><dt>Characters</dt><dd>{l.characters.toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt>Word units</dt><dd>{l.word_units.toLocaleString()}</dd></div>
              <div className="flex justify-between"><dt>Tokens</dt><dd>{l.tokens.toLocaleString()}</dd></div>
              <div className="flex justify-between font-semibold"><dt>Fertility X</dt><dd title={String(l.fertility)}>{l.fertility.toFixed(4)}</dd></div>
              <div className="flex justify-between"><dt>Rank</dt><dd>#{l.rank}</dd></div>
              {l.distance_from_best != null && (
                <div className="flex justify-between text-[var(--color-ink)]/50"><dt>Δ from best</dt><dd>+{l.distance_from_best.toFixed(4)}</dd></div>
              )}
            </dl>
          </div>
        ))}
      </div>
    </section>
  );
}

export function SectionPipeline() {
  const steps = [
    "Frozen Wikipedia articles",
    "Unicode NFC normalization",
    "Candidate tokenizer strategies",
    "BPE training",
    "Score-aware optimization",
    "Independent verification",
    "One final ≤10K tokenizer",
  ];
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">How SamaBPE Works</h2>
      <div className="mt-6 flex flex-col gap-2">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-indigo)]/10 text-sm font-bold text-[var(--color-indigo)]">{i + 1}</span>
            <span className="text-sm">{s}</span>
            {i < steps.length - 1 && <span className="ml-4 hidden text-[var(--color-ink)]/30 md:inline">↓</span>}
          </div>
        ))}
      </div>
    </section>
  );
}

export function SectionStrategyArena({ data, winner }: { data: StrategyComparison | null; winner: string }) {
  const rows = data?.strategies ?? [];
  if (!rows.length) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="strategies">
      <h2 className="text-2xl font-bold">Strategy Arena</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full border-collapse text-xs md:text-sm">
          <thead>
            <tr className="border-b text-left">
              {["Strategy", "Vocab", "EN", "HI", "TE", "BN", "Gap", "Score", "EN≤1.2", "Verified"].map((h) => (
                <th key={h} className="p-2 font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className={`border-b ${r.winner ? "bg-[var(--color-saffron)]/10 font-semibold" : ""}`}>
                <td className="p-2">{r.name}</td>
                <td className="p-2">{r.vocabularySize}</td>
                <td className="p-2">{r.fertility.en.toFixed(3)}</td>
                <td className="p-2">{r.fertility.hi.toFixed(3)}</td>
                <td className="p-2">{r.fertility.te.toFixed(3)}</td>
                <td className="p-2">{r.fertility.bn.toFixed(3)}</td>
                <td className="p-2">{r.gap.toFixed(4)}</td>
                <td className="p-2">{r.score.toFixed(1)}</td>
                <td className="p-2">{r.englishConstraintPassed ? "✓" : "✗"}</td>
                <td className="p-2">{r.verified ? "✓" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {winner && <p className="mt-3 text-sm">Winner (verified): <strong>{winner}</strong></p>}
    </section>
  );
}

export function SectionFairnessRace({ trace }: { trace: OptTraceStep[] }) {
  const data = trace.map((t) => ({ step: t.step, en: t.fertilities.en, hi: t.fertilities.hi, te: t.fertilities.te, bn: t.fertilities.bn }));
  if (!data.length) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">The Fairness Race</h2>
      <p className="text-sm text-[var(--color-ink)]/60">MEASURED optimization trace</p>
      <div className="card mt-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="step" label={{ value: "Iteration", position: "insideBottom", offset: -2 }} />
            <YAxis label={{ value: "Fertility X", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Legend />
            {(["en", "hi", "te", "bn"] as const).map((l) => (
              <Line key={l} type="monotone" dataKey={l} stroke={LANG_COLORS[l]} dot={false} strokeWidth={2} name={LANG_DISPLAY[l].native} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function SectionTokenEconomy({ allocation }: { allocation: Record<string, number> }) {
  const data = Object.entries(allocation).map(([name, value]) => ({ name, value }));
  const colors = ["#8b7355", "#2c3e6b", "#c45c26", "#2d5a3d", "#6b3a5c", "#4a5568", "#718096"];
  const total = data.reduce((s, d) => s + d.value, 0);
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">The 10K Token Economy</h2>
      <p className="text-sm text-[var(--color-ink)]/60">Script-category attribution (shared tokens not double-counted)</p>
      <p className="mt-1 font-mono text-xs">Total: {total.toLocaleString()} slots</p>
      <div className="card mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <XAxis type="number" />
            <YAxis type="category" dataKey="name" width={90} />
            <Tooltip />
            <Bar dataKey="value">{data.map((_, i) => <Cell key={i} fill={colors[i % colors.length]} />)}</Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function SectionRejected({ items }: { items: RejectedMerge[] }) {
  if (!items.length) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-12">
        <h2 className="text-2xl font-bold">Rejected Merges Graveyard</h2>
        <p className="mt-2 text-sm text-[var(--color-ink)]/60">No rejected merge records in current optimization trace.</p>
      </section>
    );
  }
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">Rejected Merges Graveyard</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {items.slice(0, 12).map((r, i) => (
          <div key={i} className="card font-mono text-xs">
            <div className="font-serif text-base font-semibold">{r.candidate}</div>
            <div>freq: {r.frequency}</div>
            <div>score {r.old_score.toFixed(1)} → {r.predicted_score.toFixed(1)}</div>
            <div className="mt-1 text-[var(--color-saffron)]">{r.reason}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function SectionGrapheme({ stats }: { stats: Record<string, { integrity_pct: number; split_clusters: number; total_graphemes: number }> | null }) {
  if (!stats) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">Grapheme Integrity</h2>
      <p className="mt-2 text-sm">What looks like one visible Indic character may contain multiple Unicode code points.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        {Object.entries(stats).map(([lang, g]) => (
          <div key={lang} className="card text-sm">
            <div className="font-semibold uppercase">{lang}</div>
            <div className="mt-2 font-mono text-xs">
              <div>Integrity: {g.integrity_pct}%</div>
              <div>Split clusters: {g.split_clusters}</div>
              <div>Graphemes: {g.total_graphemes.toLocaleString()}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function SectionReproduce({ stats }: { stats: Stats | null }) {
  const cmd = `git clone https://github.com/sohamzycus/neural-truth-lab.git
cd neural-truth-lab/session2
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/verify.py`;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="reproduce">
      <h2 className="text-2xl font-bold">Reproduce My Score</h2>
      <pre className="card mt-4 overflow-x-auto font-mono text-xs">{cmd}</pre>
      {stats && (
        <dl className="card mt-4 space-y-1 font-mono text-xs">
          <div>Tokenizer SHA-256: {stats.tokenizer_sha256}</div>
          {stats.corpus_hashes && Object.entries(stats.corpus_hashes).map(([l, h]) => (
            <div key={l}>{l.toUpperCase()} corpus: {h}</div>
          ))}
          <div>Denominator: NFC + Unicode whitespace split (see docs/DENOMINATOR.md)</div>
        </dl>
      )}
    </section>
  );
}

export function SectionDownloads() {
  const files = [
    "results/tokenizer.json", "results/vocab.json", "vocab.txt", "merges.txt",
    "results/stats.json", "results/verification_manifest.json",
    "results/strategy_comparison.json", "results/optimization_trace.json",
    "results/grapheme_stats.json", "results/vocab_roi.json", "results/parity_corpus.json",
    "results/manifest.sha256.json",
    "corpora/frozen/en_india.txt", "corpora/frozen/hi_india.txt",
    "corpora/frozen/te_india.txt", "corpora/frozen/bn_india.txt",
  ];
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="downloads">
      <h2 className="text-2xl font-bold">Downloads</h2>
      <div className="mt-4 flex flex-wrap gap-2">
        {files.map((f) => (
          <a key={f} className="btn text-xs" href={`/data/${f}`} download>{f.split("/").pop()}</a>
        ))}
      </div>
    </section>
  );
}

export function BudgetSimulator({ curves, actualAlloc }: { curves: SweepCurves | null; actualAlloc: Record<string, number> }) {
  if (!curves) return null;
  const enCurve = curves.per_language.en ?? [];
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-2xl font-bold">Budget Simulator</h2>
      <p className="text-sm text-[var(--color-ink)]/60">
        <span className="font-medium">PREDICTED</span> from measured vocabulary sweeps — not verified headline scores.
      </p>
      <div className="card mt-4 font-mono text-xs">Optimizer attribution: {JSON.stringify(actualAlloc)}</div>
      <div className="card mt-4 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={enCurve}>
            <XAxis dataKey="vocab_size" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="fertility" stroke={LANG_COLORS.en} name="EN fertility (measured sweep)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
