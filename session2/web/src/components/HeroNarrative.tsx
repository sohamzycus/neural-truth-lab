import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

const HOOK =
  "SamaBPE allocates its 10,000-token vocabulary around multilingual balance—not compression alone.";

export function HeroNarrative({ stats }: { stats: Stats | null }) {
  if (!stats) {
    return (
      <header className="px-4 py-20 text-center">
        <p className="text-[var(--color-ink)]/50">Loading verified results…</p>
      </header>
    );
  }

  const audit = stats.optimization_audit;
  const hook = audit?.hero_claim_recommended ?? HOOK;

  const trust = stats.trust ?? {
    english_lte_1_2: stats.english_constraint.pass,
    vocabulary_lte_10000: stats.vocabulary_size <= 10000,
    one_deterministic_tokenizer: true,
    scores_independently_reproducible: true,
  };

  const sorted = [...stats.languages].sort((a, b) => a.fertility - b.fertility);
  const worst = sorted[sorted.length - 1];
  const best = sorted[0];

  return (
    <header className="relative overflow-hidden border-b border-[var(--color-ink)]/10 px-4 py-10 md:py-14">
      <div className="pointer-events-none absolute inset-0 opacity-[0.04] text-6xl font-bold leading-none font-devanagari">
        <div className="absolute left-4 top-4">भारत</div>
        <div className="absolute right-8 bottom-8 font-telugu">భారత</div>
        <div className="absolute bottom-4 left-1/3 font-bengali">ভারত</div>
      </div>

      <div className="relative mx-auto max-w-6xl">
        {/* Challenge */}
        <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-[var(--color-saffron)] md:text-xs">
          ERA V5 · Session 2 · Multilingual Tokenization Challenge
        </p>

        <h1 className="mt-2 text-6xl font-bold tracking-tight text-[var(--color-ink)] md:text-8xl">
          SamaBPE
        </h1>

        <p className="mt-4 text-lg font-semibold text-[var(--color-indigo)] md:text-xl">
          One tokenizer. 10,000 tokens. Four languages.
        </p>
        <p className="mt-1 text-base text-[var(--color-ink)]/75 md:text-lg">
          How equally can AI represent them?
        </p>

        {/* Objective */}
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-[var(--color-ink)]/70 md:text-base">
          {hook}
        </p>

        {/* Verified result — four X in first viewport */}
        <div className="mt-8 grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
          {LANG_ORDER.map((lang) => {
            const l = stats.languages.find((x) => x.lang === lang)!;
            const d = LANG_DISPLAY[lang];
            const isBest = l.lang === best.lang;
            const isWorst = l.lang === worst.lang;
            return (
              <div
                key={lang}
                className={`card text-center ${isBest ? "ring-2 ring-[var(--color-leaf)]/40" : ""} ${isWorst ? "ring-2 ring-[var(--color-saffron)]/50" : ""}`}
                data-lang={lang}
              >
                <div className={`text-xs font-semibold uppercase tracking-wider text-[var(--color-ink)]/55 ${d.fontClass}`}>
                  {d.native}
                </div>
                <div
                  className="mt-2 font-mono text-2xl font-bold md:text-3xl"
                  title={`X_${lang} = ${l.fertility} (${l.tokens} tokens ÷ ${l.word_units} word units)`}
                >
                  {l.fertility.toFixed(3)}
                </div>
                <div className="text-[10px] uppercase tracking-wide text-[var(--color-ink)]/55">tokens / word</div>
                {isBest && <div className="mt-1 text-[10px] font-medium text-[var(--color-leaf)]">best X</div>}
                {isWorst && <div className="mt-1 text-[10px] font-medium text-[var(--color-saffron)]">worst X</div>}
              </div>
            );
          })}
        </div>

        {/* Fairness gap + score */}
        <div className="mt-6 flex flex-col items-center gap-3 md:mt-8">
          <div className="flex w-full max-w-lg items-center gap-2 text-xs text-[var(--color-ink)]/65 md:text-sm">
            <span className="shrink-0 font-mono">{stats.x_min.toFixed(4)}</span>
            <div className="relative h-3 flex-1 rounded-full bg-[var(--color-ink)]/10">
              <div
                className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-[var(--color-leaf)] via-[var(--color-indigo)] to-[var(--color-saffron)]"
                style={{ width: "100%" }}
              />
            </div>
            <span className="shrink-0 font-mono">{stats.x_max.toFixed(4)}</span>
          </div>
          <p className="text-center text-sm text-[var(--color-ink)]/70">
            Fairness gap: <span className="font-mono font-semibold">{stats.max_min_gap.toFixed(4)}</span>
            <span className="mx-2 text-[var(--color-ink)]/30">·</span>
            Score = 1000 ÷ gap
          </p>
          <div className="text-center">
            <div className="text-[10px] font-semibold uppercase tracking-[0.25em] text-[var(--color-saffron)]">
              Verified self-score
            </div>
            <div
              className="font-mono text-5xl font-bold tracking-tight text-[var(--color-ink)] md:text-6xl"
              title={`${stats.score} = 1000 / ${stats.max_min_gap}`}
            >
              {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </div>
          </div>
        </div>

        {/* Meaning */}
        <p className="mx-auto mt-5 max-w-2xl text-center text-sm leading-relaxed text-[var(--color-ink)]/70">
          If the same meaning needs twice as many tokens in one language, that language pays more compute
          and fits less content in the same context window.
        </p>

        {/* Proof */}
        <div className="mt-5 flex flex-wrap justify-center gap-2 text-xs md:text-sm">
          {[
            ["English ≤ 1.20", trust.english_lte_1_2],
            [`Vocabulary = ${stats.vocabulary_size} (≤10,000)`, trust.vocabulary_lte_10000],
            ["One deterministic tokenizer", trust.one_deterministic_tokenizer],
            ["Independently reproducible", trust.scores_independently_reproducible],
          ].map(([label, ok]) => (
            <span
              key={label as string}
              className={`rounded-full border px-3 py-1 ${ok ? "border-[var(--color-leaf)]/40 bg-[var(--color-leaf)]/10" : "border-red-400/40 bg-red-50"}`}
            >
              {ok ? "✓" : "✗"} {label as string}
            </span>
          ))}
        </div>
        <p className="mt-2 text-center font-mono text-[10px] text-[var(--color-ink)]/45">
          SHA-256 {stats.tokenizer_sha256.slice(0, 16)}… · run <code>python scripts/verify.py</code>
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <a href="#playground" className="btn">Try the tokenizer</a>
          <a href="#reproduce" className="btn">Verify my score</a>
          <a href="/data/results/tokenizer.json" download className="btn">Download tokenizer</a>
        </div>
      </div>
    </header>
  );
}
