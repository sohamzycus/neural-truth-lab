import type { ReactNode } from "react";
import type { Stats, StrategyComparison } from "../types";
import { LANG_DISPLAY } from "../types";

type StrategyRow = StrategyComparison["strategies"][number];

const STRATEGY_META: Record<
  string,
  { n: string; q: string; design: string }
> = {
  "shared-vanilla-bpe": {
    n: "01",
    q: "What happens when all four languages simply compete for one shared vocabulary?",
    design: "Pool all four corpora; learn merges by raw pair frequency on UTF-8 bytes with whitespace pretokenization.",
  },
  "allocated-monolingual-bpe": {
    n: "02",
    q: "What changes when the 10K budget is explicitly distributed across languages?",
    design: "Train separate BPE vocabularies per language with fixed slot allocation, then merge into one table.",
  },
  "weighted-shared-bpe": {
    n: "03",
    q: "Can controlled corpus exposure produce a stronger multilingual score?",
    design: "English-seeded bootstrap, then shared BPE with Indic-weighted merge-pair frequencies across one merge table.",
  },
  "grapheme-aware-bpe": {
    n: "04",
    q: "Does respecting writing structure change tokenization efficiency?",
    design: "Pretokenize with Unicode extended grapheme clusters as atomic units before BPE merge learning.",
  },
  "score-directed-adaptive-bpe": {
    n: "05",
    q: "Can the assignment objective itself guide each merge decision?",
    design: "English-seeded vocabulary, then greedily accept merges that improve the measured gap score at each step.",
  },
};

export function SiteNav() {
  const links = [
    ["#challenge", "Challenge"],
    ["#experiment", "Experiment"],
    ["#playground", "Try It"],
    ["#reproduce", "Evidence"],
  ];
  return (
    <nav className="sticky top-0 z-20 border-b border-[var(--color-ink)]/10 bg-[var(--color-paper)]/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
        <a href="#challenge" className="font-bold text-[var(--color-indigo)]">SamaBPE</a>
        <div className="flex flex-wrap gap-3">
          {links.map(([href, label]) => (
            <a key={href} href={href} className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]">
              {label}
            </a>
          ))}
          <a
            href="https://github.com/sohamzycus/neural-truth-lab/tree/main/session2"
            className="text-[var(--color-ink)]/70 hover:text-[var(--color-indigo)]"
          >
            Code
          </a>
        </div>
      </div>
    </nav>
  );
}

export function SectionExperiment({ data }: { data: StrategyComparison | null }) {
  const rows = [...(data?.strategies ?? [])].sort((a, b) => {
    const order = Object.keys(STRATEGY_META);
    return order.indexOf(a.id) - order.indexOf(b.id);
  });
  if (!rows.length) return null;

  return (
    <section className="mx-auto max-w-6xl px-4 py-16 md:py-20" id="experiment">
      <h2 className="text-[clamp(2.25rem,5vw,3.5rem)] font-bold leading-tight">The experiment</h2>
      <p className="mt-4 max-w-3xl text-[clamp(1.125rem,2vw,1.375rem)] leading-relaxed text-[var(--color-ink)]/80">
        One score. Multiple ways to build the tokenizer.
      </p>
      <p className="mt-2 max-w-3xl text-base text-[var(--color-ink)]/70">
        Instead of assuming one BPE design was best, SamaBPE tested multiple strategies against exactly the
        same four corpora, vocabulary budget, denominator and scoring formula.
      </p>
      <p className="mt-4 text-base font-semibold text-[var(--color-indigo)]">
        Same benchmark. Same 10K budget. Real competition. One actual winner.
      </p>

      <ol className="relative mt-14 space-y-0">
        {rows.map((s, i) => (
          <StrategyStep key={s.id} s={s} isLast={i === rows.length - 1} />
        ))}
      </ol>
    </section>
  );
}

function StrategyStep({ s, isLast }: { s: StrategyRow; isLast: boolean }) {
  const meta = STRATEGY_META[s.id] ?? { n: "—", q: s.name, design: "" };
  return (
    <li className="relative grid gap-4 pb-14 md:grid-cols-[4rem_1fr] md:gap-8">
      <div className="flex flex-col items-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-[var(--color-indigo)] bg-white font-mono text-lg font-bold tabular-nums text-[var(--color-indigo)]">
          {meta.n}
        </span>
        {!isLast && <div className="mt-2 hidden w-px flex-1 bg-[var(--color-indigo)]/25 md:block" aria-hidden />}
      </div>
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="text-xl font-bold md:text-2xl">{s.name}</h3>
          <span className="rounded bg-[var(--color-indigo)]/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-[var(--color-indigo)]">
            MEASURED
          </span>
        </div>
        <p className="mt-2 text-base font-medium text-[var(--color-ink)]/80">{meta.q}</p>
        <dl className="mt-4 space-y-3 text-sm">
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--color-saffron)]">Hypothesis</dt>
            <dd className="mt-0.5 text-[var(--color-ink)]/75">{meta.q}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--color-indigo)]">Design</dt>
            <dd className="mt-0.5 text-[var(--color-ink)]/75">{meta.design}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--color-leaf)]">Result</dt>
            <dd className="mt-1 font-mono text-sm tabular-nums">
              Score <strong>{s.score.toFixed(1)}</strong> · gap {s.gap.toFixed(4)} · EN {s.fertility.en.toFixed(3)} ·
              HI {s.fertility.hi.toFixed(3)} · TE {s.fertility.te.toFixed(3)} · BN {s.fertility.bn.toFixed(3)}
              {!s.englishConstraintPassed && (
                <span className="text-[var(--color-saffron)]"> · English constraint FAIL</span>
              )}
            </dd>
          </div>
        </dl>
      </div>
    </li>
  );
}

export function SectionWinner({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  return (
    <section
      className="border-y-2 border-[var(--color-saffron)] bg-[var(--color-saffron)]/[0.06] px-4 py-16 md:py-20"
      id="winner"
    >
      <div className="mx-auto max-w-6xl text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-[var(--color-saffron)]">
          And the winner was…
        </p>
        <h2 className="mt-3 text-[clamp(2.5rem,6vw,4rem)] font-extrabold">Weighted Shared BPE</h2>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-[var(--color-ink)]/85">
          No algorithm wins by sounding clever. The winner achieved the highest valid measured score under the
          same frozen benchmark and constraints. Score-directed adaptive BPE was tested but did not outperform
          this result.
        </p>
        <p className="mt-2 text-xs uppercase tracking-wide text-[var(--color-leaf)]">VERIFIED · results/stats.json</p>
        <p className="mt-8 font-mono text-[clamp(3.5rem,9vw,6rem)] font-extrabold leading-none tabular-nums">
          {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </p>
        <p className="mt-2 font-mono text-lg tabular-nums text-[var(--color-ink)]/60">
          gap {stats.max_min_gap.toFixed(4)} · vocab {stats.vocabulary_size.toLocaleString()}
        </p>
        <dl className="mx-auto mt-10 grid max-w-3xl grid-cols-2 gap-6 font-mono text-sm md:grid-cols-4">
          {stats.languages.map((l) => (
            <div key={l.lang}>
              <dt className={`text-[var(--color-ink)]/55 ${LANG_DISPLAY[l.lang]?.fontClass ?? ""}`}>
                {LANG_DISPLAY[l.lang]?.native ?? l.label}
              </dt>
              <dd className="text-xl font-bold tabular-nums">{l.fertility.toFixed(4)}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}

export function SectionWhyWinner({
  stats,
  strategies,
}: {
  stats: Stats | null;
  strategies: StrategyComparison | null;
}) {
  if (!stats) return null;
  const vanilla = strategies?.strategies?.find((s) => s.id === "shared-vanilla-bpe");
  const vanillaGap = vanilla?.gap?.toFixed(4) ?? "—";
  return (
    <section className="mx-auto max-w-6xl px-4 py-14" id="understand">
      <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">Why it won</h2>
      <ul className="mt-5 max-w-3xl space-y-3 text-[clamp(1rem,1.5vw,1.125rem)] leading-relaxed text-[var(--color-ink)]/85">
        <li>
          Achieved the smallest measured X<sub>max</sub> − X<sub>min</sub> spread among valid candidates (verified
          gap {stats.max_min_gap.toFixed(4)}).
        </li>
        {vanilla && (
          <li>
            Beat vanilla shared BPE on train-arena gap ({vanillaGap} vs final verified{" "}
            {stats.max_min_gap.toFixed(4)}).
          </li>
        )}
        <li>One shared merge table for all four languages — no runtime language routing.</li>
        <li>
          English-seeded bootstrap with Indic-weighted pair selection; final artefact{" "}
          <code className="font-mono text-sm">en_bootstrap=6400</code> (submission_metadata.json).
        </li>
      </ul>
      <p className="mt-4 text-sm text-[var(--color-ink)]/55">
        Correlation from measured results — not proof of causality beyond the benchmark.
      </p>
    </section>
  );
}

export function SectionVocabularyEconomy({ stats }: { stats: Stats | null }) {
  if (!stats) return null;
  const alloc = stats.vocab_attribution ?? stats.vocab_allocation ?? {};
  const total = Object.values(alloc).reduce((a, b) => a + (typeof b === "number" ? b : 0), 0);
  return (
    <section className="mx-auto max-w-6xl px-4 py-16 md:py-20" id="economy">
      <h2 className="text-[clamp(2.25rem,5vw,3.5rem)] font-bold">The 10,000-token economy</h2>
      <p className="mt-4 max-w-3xl text-[clamp(1.0625rem,1.8vw,1.25rem)] leading-relaxed text-[var(--color-ink)]/80">
        A BPE vocabulary is a fixed budget. Every learned token consumes capacity. Across four languages and
        four scripts, those {stats.vocabulary_size.toLocaleString()} slots determine what can be represented
        compactly on the frozen corpora.
      </p>
      <p className="mt-2 text-sm text-[var(--color-ink)]/55">
        Script attribution is heuristic — tokens may appear across multiple languages.
      </p>
      <table className="mt-8 w-full max-w-xl text-left font-mono text-sm">
        <thead>
          <tr className="border-b border-[var(--color-ink)]/15 text-xs uppercase tracking-wide text-[var(--color-ink)]/50">
            <th className="py-2 font-semibold">Script bucket</th>
            <th className="py-2 text-right font-semibold">Tokens</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(alloc).map(([k, v]) => (
            <tr key={k} className="border-b border-[var(--color-ink)]/8">
              <td className="py-2">{k}</td>
              <td className="py-2 text-right tabular-nums font-semibold">{v}</td>
            </tr>
          ))}
          <tr className="font-semibold">
            <td className="pt-3">Total</td>
            <td className="pt-3 text-right tabular-nums">{total}</td>
          </tr>
        </tbody>
      </table>
    </section>
  );
}

export function SectionExploreLab({ children }: { children: ReactNode }) {
  return (
    <section className="mx-auto max-w-6xl px-4 py-12" id="explore-lab">
      <details>
        <summary className="cursor-pointer text-[clamp(1.5rem,3vw,2rem)] font-bold text-[var(--color-indigo)]">
          Explore the lab
        </summary>
        <p className="mt-2 text-sm text-[var(--color-ink)]/60">
          Optimization traces, ROI estimates, grapheme checks, and experiments that did not win.
        </p>
        <div className="mt-8 space-y-10 border-t border-[var(--color-ink)]/10 pt-8">{children}</div>
      </details>
    </section>
  );
}
