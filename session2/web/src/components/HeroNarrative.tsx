import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

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
    <header className="border-b border-[var(--color-ink)]/10 px-4 py-10 md:py-14" id="challenge">
      <div className="mx-auto max-w-6xl">
        <h1 className="font-sans text-[clamp(4rem,9vw,6.5rem)] font-bold leading-none tracking-tight">
          SamaBPE
        </h1>
        <p className="mt-4 text-[clamp(1.5rem,3vw,2.5rem)] font-semibold text-[var(--color-indigo)]">
          One vocabulary. Four scripts. 10,000 tokens.
        </p>
        <p className="mt-3 max-w-3xl text-[clamp(1.125rem,2vw,1.375rem)] leading-relaxed text-[var(--color-ink)]/80">
          Can a single BPE tokenizer represent English, हिन्दी, తెలుగు and বাংলা efficiently under the
          same scoring constraint?
        </p>
        <ul className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-sm text-[var(--color-ink)]/65">
          <li>One tokenizer · ≤10,000 vocabulary</li>
          <li>English X ≤ 1.2</li>
          <li>Maximize 1000 ÷ (X<sub>max</sub> − X<sub>min</sub>)</li>
        </ul>

        <div className="mt-10">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-saffron)]">Verified result</p>
          <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
            {LANG_ORDER.map((lang) => {
              const l = stats.languages.find((x) => x.lang === lang)!;
              const d = LANG_DISPLAY[lang];
              return (
                <div key={lang} className="text-center" data-lang={lang}>
                  <div className={`text-sm font-semibold ${d.fontClass}`}>{d.native}</div>
                  <div className="mt-1 font-mono text-[clamp(2rem,4.5vw,3rem)] font-bold tabular-nums">
                    {l.fertility.toFixed(4)}
                  </div>
                  <div className="text-xs text-[var(--color-ink)]/55">tokens / word unit</div>
                  <div className="mt-1 font-mono text-xs tabular-nums text-[var(--color-ink)]/45">
                    {l.tokens.toLocaleString()} ÷ {l.word_units.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-[var(--color-ink)]/60">
            Verified gap <span className="font-mono font-semibold tabular-nums">{stats.max_min_gap.toFixed(4)}</span>
          </p>
          <div className="mt-2 font-mono text-[clamp(3rem,7vw,5rem)] font-bold tabular-nums">
            {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
          <p className="text-sm text-[var(--color-ink)]/55">1000 ÷ {stats.max_min_gap.toFixed(4)}</p>
        </div>

        <details className="mx-auto mt-6 max-w-2xl text-center text-sm">
          <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">What is X?</summary>
          <p className="mt-2 text-[var(--color-ink)]/75">
            X measures tokenizer fertility: encoded BPE tokens divided by word units in the complete frozen
            article. Word units = NFC normalize → split on Unicode whitespace → discard empty segments
            (<code className="font-mono text-xs">python/samabpe/word_units.py::count_word_units</code>).
          </p>
        </details>

        <div className="mt-6 flex flex-wrap justify-center gap-2 text-sm">
          {[
            ["English ≤ 1.20", trust.english_lte_1_2],
            ["Vocabulary ≤ 10,000", trust.vocabulary_lte_10000],
            ["One tokenizer", trust.one_deterministic_tokenizer],
            ["Reproducible", trust.scores_independently_reproducible],
          ].map(([label, ok]) => (
            <span key={label as string} className={`rounded-full border px-3 py-1 text-xs ${ok ? "border-[var(--color-leaf)]/40" : "border-red-300"}`}>
              {ok ? "✓" : "✗"} {label as string}
            </span>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <a href="#experiment" className="btn">See the experiment</a>
          <a href="#playground" className="btn">Try the tokenizer</a>
          <a href="#reproduce" className="btn">Verify the score</a>
        </div>
      </div>
    </header>
  );
}
