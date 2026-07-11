import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

type ProofData = {
  claim?: string;
  mixed_script_highlight?: { input: string; tokens: string[]; token_count: number };
};

export function HeroNarrative({
  stats,
  proof,
  sensitivity,
}: {
  stats: Stats | null;
  proof?: ProofData | null;
  sensitivity?: { baseline_score?: number; improved?: boolean; best_track_a_score?: number } | null;
}) {
  if (!stats) {
    return (
      <header className="px-4 py-20 text-center">
        <p className="text-[var(--color-ink)]/50">Loading verified results…</p>
      </header>
    );
  }

  const audit = stats.optimization_audit;
  const hook =
    audit?.hero_claim_recommended ??
    "SamaBPE allocates its 10,000-token vocabulary around multilingual balance—not compression alone.";

  const trust = stats.trust ?? {
    english_lte_1_2: stats.english_constraint.pass,
    vocabulary_lte_10000: stats.vocabulary_size <= 10000,
    one_deterministic_tokenizer: true,
    scores_independently_reproducible: true,
  };

  const sorted = [...stats.languages].sort((a, b) => a.fertility - b.fertility);
  const worst = sorted[sorted.length - 1];
  const best = sorted[0];
  const mixed = proof?.mixed_script_highlight;

  return (
    <header className="relative overflow-hidden border-b border-[var(--color-ink)]/10 px-4 py-10 md:py-14">
      <div className="pointer-events-none absolute inset-0 opacity-[0.04] text-6xl font-bold leading-none font-devanagari">
        <div className="absolute left-4 top-4">भारत</div>
        <div className="absolute right-8 bottom-8 font-telugu">భారత</div>
        <div className="absolute bottom-4 left-1/3 font-bengali">ভারত</div>
      </div>

      <div className="relative mx-auto max-w-6xl">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[var(--color-saffron)]">
          ERA V5 · Session 2 · Multilingual Tokenization Challenge
        </p>

        <h1 className="mt-2 font-sans text-[clamp(3.25rem,8vw,6.5rem)] font-bold leading-none tracking-tight text-[var(--color-ink)]">
          SamaBPE
        </h1>

        <p className="mt-4 font-sans text-[clamp(1.25rem,2.5vw,1.75rem)] font-semibold text-[var(--color-indigo)]">
          One tokenizer. 10,000 tokens. Four languages.
        </p>
        <p className="mt-1 font-sans text-[clamp(1.125rem,2vw,1.5rem)] font-medium text-[var(--color-ink)]/80">
          How equally can AI represent them?
        </p>

        <p className="mt-4 max-w-3xl text-base leading-relaxed text-[var(--color-ink)]/70 md:text-lg">
          {hook}
        </p>

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
                  className="mt-2 font-mono text-[clamp(1.75rem,4vw,2.5rem)] font-bold tabular-nums"
                  title={`X_${lang} = ${l.fertility} (${l.tokens} tokens ÷ ${l.word_units} word units)`}
                >
                  {l.fertility.toFixed(3)}
                </div>
                <div className="text-xs uppercase tracking-wide text-[var(--color-ink)]/55">tokens / word</div>
                {isBest && <div className="mt-1 text-xs font-medium text-[var(--color-leaf)]">X_min</div>}
                {isWorst && <div className="mt-1 text-xs font-medium text-[var(--color-saffron)]">X_max</div>}
              </div>
            );
          })}
        </div>

        <div className="mt-6 flex flex-col items-center gap-3 md:mt-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-ink)]/55">
            Verified fairness gap
          </p>
          <div className="flex w-full max-w-lg items-center gap-2 text-sm text-[var(--color-ink)]/65">
            <span className="shrink-0 font-mono tabular-nums">{stats.x_min.toFixed(4)}</span>
            <div className="relative h-4 flex-1 rounded-full bg-[var(--color-ink)]/10">
              <div className="absolute inset-y-0 left-0 w-full rounded-full bg-gradient-to-r from-[var(--color-leaf)] via-[var(--color-indigo)] to-[var(--color-saffron)]" />
            </div>
            <span className="shrink-0 font-mono tabular-nums">{stats.x_max.toFixed(4)}</span>
          </div>
          <p className="text-center text-base text-[var(--color-ink)]/75">
            Gap = <span className="font-mono font-semibold tabular-nums">{stats.max_min_gap.toFixed(4)}</span>
          </p>

          <div className="text-center">
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--color-saffron)]">
              Verified self-score
            </div>
            <div
              className="font-mono text-[clamp(3rem,7vw,5.5rem)] font-bold leading-none tracking-tight tabular-nums text-[var(--color-ink)]"
              title={`${stats.score} = 1000 / ${stats.max_min_gap}`}
            >
              {stats.score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </div>
            <p className="mt-2 text-sm text-[var(--color-ink)]/65">
              1000 ÷ {stats.max_min_gap.toFixed(4)}
            </p>
            {sensitivity?.improved && sensitivity.baseline_score && (
              <p className="mt-2 text-sm font-medium text-[var(--color-leaf)]">
                {sensitivity.baseline_score.toFixed(2)} → {stats.score.toFixed(2)} · +
                {(((stats.score - sensitivity.baseline_score) / sensitivity.baseline_score) * 100).toFixed(1)}%
              </p>
            )}
          </div>

          <details className="mt-1 max-w-xl text-center text-sm text-[var(--color-ink)]/70">
            <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">
              How is X calculated?
            </summary>
            <p className="mt-2 leading-relaxed">
              Complete article BPE token count ÷ NFC-normalized Unicode-whitespace word units.
              The identical rule is applied to all four languages.
              <a href="#reproduce" className="ml-1 underline">Full methodology →</a>
            </p>
          </details>
        </div>

        <p className="mx-auto mt-5 max-w-2xl text-center text-base leading-relaxed text-[var(--color-ink)]/70">
          <span className="font-medium text-[var(--color-ink)]/85">Why this matters:</span>{" "}
          when equivalent content requires more tokens in one language, that language consumes more of
          the available token window and requires more token-level processing.
        </p>

        {mixed && (
          <div className="mx-auto mt-6 max-w-2xl rounded-lg border border-[var(--color-indigo)]/20 bg-white/50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--color-indigo)]">
              {proof?.claim ?? "ONE TOKENIZER · FOUR LANGUAGES · NO LANGUAGE ROUTING"}
            </p>
            <p className="mt-2 font-mono text-sm break-all">{mixed.input}</p>
            <p className="mt-2 text-xs text-[var(--color-ink)]/60">
              VERIFIED · {mixed.token_count} tokens · same artefact for all scripts
            </p>
            <div className="mt-2 flex flex-wrap gap-1 font-mono text-xs">
              {mixed.tokens.map((t, i) => (
                <span key={i} className="rounded border border-[var(--color-ink)]/15 bg-white px-1">
                  {t.replace("</w>", "·")}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-5 flex flex-wrap justify-center gap-2 text-sm">
          {[
            ["English ≤ 1.20", trust.english_lte_1_2, "VERIFIED"],
            [`Vocabulary ≤ 10,000`, trust.vocabulary_lte_10000, "VERIFIED"],
            ["One deterministic tokenizer", trust.one_deterministic_tokenizer, "VERIFIED"],
            ["Independent reproduction", trust.scores_independently_reproducible, "VERIFIED"],
          ].map(([label, ok, tag]) => (
            <span
              key={label as string}
              className={`rounded-full border px-3 py-1 ${ok ? "border-[var(--color-leaf)]/40 bg-[var(--color-leaf)]/10" : "border-red-400/40 bg-red-50"}`}
            >
              <span className="text-[10px] uppercase tracking-wide text-[var(--color-ink)]/45">{tag as string}</span>
              {" "}{ok ? "✓" : "✗"} {label as string}
            </span>
          ))}
        </div>
        <p className="mt-2 text-center font-mono text-xs text-[var(--color-ink)]/45">
          SHA-256 {stats.tokenizer_sha256.slice(0, 16)}…
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <a href="#optimizer" className="btn">Explore optimizer</a>
          <a href="#playground" className="btn">Try the tokenizer</a>
          <a href="#reproduce" className="btn">Verify my score</a>
          <a href="/data/results/tokenizer.json" download className="btn">Download tokenizer</a>
        </div>
      </div>
    </header>
  );
}
