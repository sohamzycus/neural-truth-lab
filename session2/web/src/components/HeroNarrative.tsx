import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

export function HeroNarrative({ stats }: { stats: Stats | null }) {
  if (!stats) {
    return (
      <header className="px-4 py-20 text-center">
        <p className="text-[var(--color-ink)]/50">Loading verified results…</p>
      </header>
    );
  }

  const trust = stats.trust ?? {
    english_lte_1_2: stats.english_constraint.pass,
    vocabulary_lte_10000: stats.vocabulary_size <= 10000,
    one_deterministic_tokenizer: true,
    scores_independently_reproducible: true,
  };

  return (
    <header className="relative overflow-hidden border-b border-[var(--color-ink)]/10 px-4 py-12 md:py-16">
      <div className="pointer-events-none absolute inset-0 opacity-[0.03] text-7xl font-bold leading-none">
        <div className="absolute left-4 top-4">भारत</div>
        <div className="absolute right-8 bottom-8">భారత</div>
        <div className="absolute bottom-4 left-1/3">ভারত</div>
      </div>

      <div className="relative mx-auto max-w-6xl">
        <p className="text-xs font-medium uppercase tracking-[0.25em] text-[var(--color-saffron)]">
          ERA V5 · Session 2 · Multilingual Tokenization Challenge
        </p>
        <h1 className="mt-3 text-5xl font-bold tracking-tight md:text-6xl">SamaBPE</h1>
        <p className="mt-4 max-w-3xl text-xl text-[var(--color-ink)]/85 md:text-2xl">
          Most tokenizers optimize frequency. <em>SamaBPE optimizes fairness.</em>
        </p>
        <p className="mt-4 max-w-3xl text-base leading-relaxed text-[var(--color-ink)]/70">
          One deterministic 10,000-token BPE vocabulary must encode the Wikipedia <em>India</em> article
          in English, Hindi, Telugu and Bengali. The challenge is to keep all four languages equally
          token-efficient while English stays at or below 1.20 tokens per word.
        </p>

        {/* 30-second explainer */}
        <div className="mt-8 rounded-lg border border-[var(--color-indigo)]/20 bg-white/50 p-4 md:p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-indigo)]">
            Understand the challenge in 30 seconds
          </h2>
          <ol className="mt-3 grid gap-2 text-sm md:grid-cols-3">
            <li><strong>1. TOKENIZE</strong> — The same article is encoded in four languages.</li>
            <li><strong>2. MEASURE</strong> — For each language: tokens ÷ words = X.</li>
            <li><strong>3. BALANCE</strong> — The closer the best and worst X, the higher the score.</li>
          </ol>
          <p className="mt-3 text-sm italic text-[var(--color-ink)]/65">
            SamaBPE&apos;s job is not simply to make every language smaller. It is to make all four
            languages equally efficient under one 10,000-token budget.
          </p>
        </div>

        {/* Language lanes + score */}
        <div className="mt-10 grid gap-4 md:grid-cols-4">
          {LANG_ORDER.map((lang) => {
            const l = stats.languages.find((x) => x.lang === lang)!;
            const d = LANG_DISPLAY[lang];
            return (
              <div key={lang} className="card text-center" data-lang={lang}>
                <div className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">{d.native}</div>
                <div className="mt-2 font-mono text-3xl font-bold">{l.fertility.toFixed(3)}</div>
                <div className="text-xs text-[var(--color-ink)]/60">tokens / word unit</div>
                <div className="mt-2 font-mono text-xs text-[var(--color-ink)]/50">
                  {l.tokens.toLocaleString()} tokens · {l.word_units.toLocaleString()} words
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 flex flex-col items-center gap-2">
          <div className="flex items-center gap-4 text-sm text-[var(--color-ink)]/60">
            <span>Best X: {stats.x_min.toFixed(4)}</span>
            <span className="h-px w-16 bg-[var(--color-saffron)]" aria-hidden />
            <span>Gap: {stats.max_min_gap.toFixed(4)}</span>
            <span className="h-px w-16 bg-[var(--color-indigo)]" aria-hidden />
            <span>Worst X: {stats.x_max.toFixed(4)}</span>
          </div>
          <div className="mt-2 text-center">
            <div className="text-xs uppercase tracking-widest text-[var(--color-saffron)]">Verified self-score</div>
            <div className="font-mono text-4xl font-bold">{stats.score.toFixed(2)}</div>
            <div className="text-sm text-[var(--color-ink)]/60">1000 ÷ {stats.max_min_gap.toFixed(4)}</div>
          </div>
        </div>

        {/* Trust strip */}
        <div className="mt-8 flex flex-wrap justify-center gap-3 text-sm">
          {[
            ["English ≤ 1.20", trust.english_lte_1_2],
            ["Vocabulary ≤ 10,000", trust.vocabulary_lte_10000],
            ["One deterministic tokenizer", trust.one_deterministic_tokenizer],
            ["Scores independently reproducible", trust.scores_independently_reproducible],
          ].map(([label, ok]) => (
            <span
              key={label as string}
              className={`rounded-full border px-3 py-1 ${ok ? "border-[var(--color-leaf)]/40 bg-[var(--color-leaf)]/10" : "border-red-400/40 bg-red-50"}`}
            >
              {ok ? "✓" : "✗"} {label as string}
            </span>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <a href="#playground" className="btn">Try the tokenizer</a>
          <a href="#reproduce" className="btn">Verify my score</a>
          <a href="/data/results/tokenizer.json" download className="btn">Download tokenizer</a>
        </div>

        <p className="mx-auto mt-6 max-w-2xl text-center text-sm text-[var(--color-ink)]/65">
          <strong>Why this matters:</strong> if the same meaning needs twice as many tokens in one language,
          that language effectively pays more in compute and fits less information into the same context window.
        </p>
      </div>
    </header>
  );
}
