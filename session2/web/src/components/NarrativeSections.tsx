import type { ReactNode } from "react";
import type { Stats, StrategyComparison } from "../types";
import { LANG_DISPLAY } from "../types";

const STRATEGY_COPY: Record<string, { n: string; q: string }> = {
  "shared-vanilla-bpe": {
    n: "01",
    q: "What happens when all four languages simply compete for one shared vocabulary?",
  },
  "allocated-monolingual-bpe": {
    n: "02",
    q: "What changes when vocabulary capacity is explicitly allocated across languages?",
  },
  "weighted-shared-bpe": {
    n: "03",
    q: "Can adjusted corpus exposure improve the min–max fertility spread?",
  },
  "grapheme-aware-bpe": {
    n: "04",
    q: "Does respecting script-level writing structure change tokenization behaviour?",
  },
  "score-directed-adaptive-bpe": {
    n: "05",
    q: "Can the assignment scoring rule itself influence merge decisions?",
  },
};

export function SiteNav() {
  const links = [
    ["#challenge", "The Challenge"],
    ["#experiment", "The Experiment"],
    ["#playground", "Try It"],
    ["#reproduce", "Evidence"],
  ];
  return (
    <nav className="sticky top-0 z-20 border-b border-[var(--color-ink)]/10 bg-[var(--color-paper)]/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
        <a href="#challenge" className="font-bold text-[var(--color-indigo)]">SamaBPE</a>
        <div className="flex flex-wrap gap-3">
          {links.map(([href, label]) => (
            <a key={href} href={href} className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]">{label}</a>
          ))}
          <a href="https://github.com/sohamzycus/neural-truth-lab/tree/main/session2" className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]">Code</a>
        </div>
      </div>
    </nav>
  );
}

export function SectionExperiment({ data }: { data: StrategyComparison | null }) {
  const rows = data?.strategies ?? [];
  if (!rows.length) return null;
  return (
    <section className="mx-auto max-w-6xl px-4 py-14" id="experiment">
      <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">The experiment</h2>
      <p className="mt-3 max-w-3xl text-lg text-[var(--color-ink)]/75">
        One score. Multiple ways to build the tokenizer. SamaBPE trained and measured each strategy on
        the same four frozen corpora, the same word-unit rule, the same 10,000-token budget, and the
        same scoring formula.
      </p>
      <ol className="mt-10 space-y-8 border-l-2 border-[var(--color-indigo)]/20 pl-6">
        {rows.map((s) => {
          const copy = STRATEGY_COPY[s.id] ?? { n: "—", q: s.name };
          return (
            <li key={s.id}>
              <p className="text-xs font-semibold uppercase tracking-wider text-[var(--color-indigo)]">
                {copy.n} · <span className="rounded bg-[var(--color-indigo)]/10 px-1.5 py-0.5">MEASURED</span>
              </p>
              <h3 className="mt-1 text-xl font-semibold">{s.name}</h3>
              <p className="mt-1 text-[var(--color-ink)]/70">{copy.q}</p>
              <p className="mt-3 font-mono text-sm tabular-nums">
                Score {s.score.toFixed(1)} · gap {s.gap.toFixed(4)} · EN {s.fertility.en.toFixed(3)} ·
                HI {s.fertility.hi.toFixed(3)} · TE {s.fertility.te.toFixed(3)} · BN {s.fertility.bn.toFixed(3)}
                {s.englishConstraintPassed ? "" : " · English constraint FAIL"}
              </p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

export function SectionWinner({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  return (
    <section className="mx-auto max-w-6xl border-y border-[var(--color-saffron)]/30 bg-[var(--color-saffron)]/5 px-4 py-14" id="winner">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--color-saffron)]">And the winner was…</p>
      <h2 className="mt-2 text-[clamp(2.25rem,5vw,3.5rem)] font-bold">Weighted Shared BPE</h2>
      <p className="mt-4 max-w-3xl text-lg text-[var(--color-ink)]/80">
        The final tokenizer was not chosen because its algorithm sounded more advanced. It won because
        it achieved the highest valid score on the frozen benchmark under the assignment constraints.
        Score-directed adaptive BPE was evaluated but did not outperform this result.
      </p>
      <p className="mt-2 text-xs uppercase tracking-wide text-[var(--color-leaf)]">VERIFIED · results/stats.json</p>
      <dl className="mt-6 grid gap-4 font-mono text-sm sm:grid-cols-2 lg:grid-cols-4">
        {stats.languages.map((l) => (
          <div key={l.lang}>
            <dt className={`text-[var(--color-ink)]/55 ${LANG_DISPLAY[l.lang]?.fontClass ?? ""}`}>
              {LANG_DISPLAY[l.lang]?.native ?? l.label}
            </dt>
            <dd className="text-2xl font-bold tabular-nums">{l.fertility.toFixed(4)}</dd>
            <dd className="text-xs text-[var(--color-ink)]/50">{l.tokens} tokens · {l.word_units} word units</dd>
          </div>
        ))}
      </dl>
      <p className="mt-6 font-mono text-3xl font-bold tabular-nums">
        Score {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        <span className="ml-4 text-base font-normal text-[var(--color-ink)]/60">gap {stats.max_min_gap.toFixed(4)}</span>
      </p>
    </section>
  );
}

export function SectionWhyWinner({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  const vanillaGap = 0.7229;
  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h2 className="text-[clamp(1.75rem,3vw,2.5rem)] font-bold">Why it won</h2>
      <ul className="mt-4 max-w-3xl space-y-3 text-base text-[var(--color-ink)]/80">
        <li>English-seeded bootstrap plus Indic-weighted merge selection beat vanilla shared BPE on the measured gap ({vanillaGap.toFixed(4)} → {stats.max_min_gap.toFixed(4)}).</li>
        <li>All four languages share one merge table — no runtime language routing.</li>
        <li>Final artefact uses <code className="font-mono text-sm">en_bootstrap=6400</code> (see submission_metadata.json) while satisfying English X ≤ 1.2.</li>
        <li>Allocated monolingual and grapheme-aware strategies failed the English constraint or scored far lower in the train arena.</li>
      </ul>
      <p className="mt-4 text-sm text-[var(--color-ink)]/55">MEASURED train-arena + VERIFIED final submission. See experiment journal in README.</p>
    </section>
  );
}

export function SectionVocabularyEconomy({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  const alloc = stats.vocab_attribution ?? stats.vocab_allocation ?? {};
  return (
    <section className="mx-auto max-w-6xl px-4 py-14" id="economy">
      <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">The 10,000-token economy</h2>
      <p className="mt-3 max-w-3xl text-lg text-[var(--color-ink)]/75">
        A BPE vocabulary is a fixed budget. Every learned token consumes capacity. Across four languages
        and four scripts, those 10,000 slots determine what can be represented compactly on the frozen
        Wikipedia India corpora.
      </p>
      <p className="mt-2 text-sm text-[var(--color-ink)]/55">
        Script attribution is heuristic (first-character script of each token) — not a hard language assignment.
      </p>
      <div className="mt-6 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(alloc).map(([k, v]) => (
          <div key={k} className="flex justify-between border-b border-[var(--color-ink)]/10 py-2 font-mono text-sm">
            <span>{k}</span>
            <span className="tabular-nums font-semibold">{v}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function SectionExploreLab({ children }: { children: ReactNode }) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="explore-lab">
      <details className="group">
        <summary className="cursor-pointer text-[clamp(1.5rem,3vw,2rem)] font-bold text-[var(--color-indigo)]">
          Explore the lab
        </summary>
        <p className="mt-2 text-sm text-[var(--color-ink)]/60">
          Secondary research artefacts — optimization traces, ROI estimates, grapheme checks, and failed experiments.
        </p>
        <div className="mt-6 space-y-8 opacity-90">{children}</div>
      </details>
    </section>
  );
}
