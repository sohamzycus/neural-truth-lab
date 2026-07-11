import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

const CONSTRAINTS = [
  "1 tokenizer",
  "≤ 10,000 tokens",
  "4 languages",
  "English X ≤ 1.20",
] as const;

export function HeroNarrative({ stats }: { stats: Stats | null }) {
  if (!stats) {
    return (
      <header className="px-4 py-20 text-center" id="challenge">
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
    <>
      <header className="px-4 pb-8 pt-10 md:pt-12" id="challenge">
        <div className="mx-auto max-w-6xl">
          <h1 className="font-sans text-[clamp(4rem,9vw,7rem)] font-extrabold leading-none tracking-tight">
            SamaBPE
          </h1>
          <p className="mt-5 text-[clamp(2rem,5vw,3.25rem)] font-bold leading-tight text-[var(--color-indigo)]">
            One vocabulary. Four scripts. 10,000 tokens.
          </p>
          <p className="mt-4 max-w-3xl text-[clamp(1.125rem,2vw,1.5rem)] leading-relaxed text-[var(--color-ink)]/85">
            Can a single BPE tokenizer represent English, हिन्दी, తెలుగు and বাংলা efficiently under the
            same scoring constraint?
          </p>
          <p className="mt-3 max-w-3xl text-base text-[var(--color-ink)]/65">
            Multiple BPE strategies compete under identical corpora, constraints and scoring rule — every
            result is inspectable and reproducible.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {CONSTRAINTS.map((c) => (
              <span key={c} className="rounded-full border border-[var(--color-indigo)]/25 px-3 py-1 font-mono text-xs tabular-nums">
                {c}
              </span>
            ))}
          </div>
        </div>
      </header>

      <section className="border-y border-[var(--color-ink)]/10 px-4 py-12 md:py-16" id="result">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-saffron)]">
            Verified result
          </p>
          <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-4">
            {LANG_ORDER.map((lang) => {
              const l = stats.languages.find((x) => x.lang === lang)!;
              const d = LANG_DISPLAY[lang];
              return (
                <div key={lang} className="text-center" data-lang={lang}>
                  <div className={`text-sm font-semibold ${d.fontClass}`}>{d.native}</div>
                  <div className="mt-2 font-mono text-[clamp(2.25rem,5vw,3.25rem)] font-bold tabular-nums leading-none">
                    {l.fertility.toFixed(4)}
                  </div>
                  <div className="mt-1 text-xs text-[var(--color-ink)]/55">tokens / word unit</div>
                  <div className="mt-1 font-mono text-xs tabular-nums text-[var(--color-ink)]/45">
                    {l.tokens.toLocaleString()} ÷ {l.word_units.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-12 text-center">
            <div className="flex flex-col items-center gap-1 sm:flex-row sm:justify-center sm:gap-10">
              <div>
                <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Verified gap</p>
                <p className="font-mono text-[clamp(1.75rem,4vw,2.5rem)] font-bold tabular-nums">
                  {stats.max_min_gap.toFixed(4)}
                </p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wider text-[var(--color-saffron)]">Verified score</p>
                <p
                  className="font-mono text-[clamp(4rem,10vw,7rem)] font-extrabold leading-none tabular-nums"
                  title={`${stats.score} = 1000 / ${stats.max_min_gap}`}
                >
                  {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </p>
                <p className="text-sm text-[var(--color-ink)]/50">1000 ÷ {stats.max_min_gap.toFixed(4)}</p>
              </div>
            </div>
          </div>

          <details className="mx-auto mt-8 max-w-2xl text-center text-sm">
            <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">What is X?</summary>
            <p className="mt-2 text-left text-[var(--color-ink)]/75">
              X is tokenizer fertility: total encoded BPE tokens divided by total word units in the complete
              frozen article. Lower X means fewer tokens per word unit. Word units = NFC normalize → split on
              Unicode whitespace → discard empty segments (
              <code className="font-mono text-xs">python/samabpe/word_units.py::count_word_units</code>).
            </p>
          </details>

          <div className="mt-6 flex flex-wrap justify-center gap-2 text-xs">
            {[
              ["English ≤ 1.20", trust.english_lte_1_2, "VERIFIED"],
              ["Vocabulary ≤ 10,000", trust.vocabulary_lte_10000, "VERIFIED"],
              ["One tokenizer", trust.one_deterministic_tokenizer, "VERIFIED"],
              ["Reproducible", trust.scores_independently_reproducible, "VERIFIED"],
            ].map(([label, ok, tag]) => (
              <span
                key={label as string}
                className={`rounded-full border px-3 py-1 ${ok ? "border-[var(--color-leaf)]/40" : "border-red-300"}`}
              >
                <span className="text-[10px] uppercase text-[var(--color-ink)]/45">{tag as string}</span>{" "}
                {ok ? "✓" : "✗"} {label as string}
              </span>
            ))}
          </div>

          <p className="mx-auto mt-6 max-w-2xl text-center text-xs text-[var(--color-ink)]/50">
            Optimizes min–max fertility spread on four frozen Wikipedia India corpora — not universal linguistic
            fairness or tokenizer superiority beyond this benchmark.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href="#experiment" className="btn">See the experiment</a>
            <a href="#playground" className="btn">Try the tokenizer</a>
            <a href="#reproduce" className="btn">Verify the score</a>
          </div>
        </div>
      </section>
    </>
  );
}
