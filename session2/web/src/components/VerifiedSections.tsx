import type { VerifiedSubmission } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

const CAT_LABELS: Record<string, string> = {
  latin_dominant: "Latin-dominant",
  devanagari_dominant: "Devanagari-dominant",
  telugu_dominant: "Telugu-dominant",
  bengali_dominant: "Bengali-dominant",
  shared_punctuation_digits_symbols: "Shared punctuation/digits/symbols",
  mixed_script: "Mixed-script",
  other_unicode: "Other Unicode",
  special_token: "Special tokens",
};

function badge(pass: boolean) {
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${pass ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"}`}>
      {pass ? "PASS" : "FAIL"}
    </span>
  );
}

export function VerifiedSubmissionPage({ data }: { data: VerifiedSubmission | null }) {
  if (!data) {
    return <p className="p-8 text-center text-[var(--color-ink)]/50">Loading verified submission data…</p>;
  }

  const m = data.metrics;
  const rev = data.fertilityExamples.reviewer_sample;
  const comp = data.vocabularyComposition;
  const util = data.vocabularyUtilization;
  const opt = data.optimizer;

  return (
    <>
      <header className="px-4 pb-4 pt-10 md:pt-12" id="challenge">
        <div className="mx-auto max-w-6xl">
          <h1 className="font-sans text-[clamp(3rem,8vw,6rem)] font-extrabold leading-none tracking-tight">SamaBPE</h1>
          <p className="mt-4 text-[clamp(1.5rem,3.5vw,2.25rem)] font-bold text-[var(--color-indigo)]">
            One faithful tokenizer. Four Wikipedia pages. 10,000 shared tokens.
          </p>
          <p className="mt-3 max-w-3xl text-base text-[var(--color-ink)]/75">
            A standard Hugging Face BPE tokenizer trained on faithful Markdown from India&apos;s Wikipedia page in
            English, Hindi, Telugu and Bengali. SamaBPE searches multilingual training exposure while preserving one
            shared, independently reproducible tokenizer.
          </p>
          <ul className="mt-6 flex flex-wrap gap-2 text-xs font-medium">
            {["Standard Hugging Face BPE", "Faithful encode → decode", "English < 1.2", "Hindi < 1.2"].map((t) => (
              <li key={t} className="rounded-full border border-[var(--color-indigo)]/25 px-3 py-1">
                {t} {t.includes("< 1.2") ? (data.thresholds[t.startsWith("English") ? "en_under_1_2" : "hi_under_1_2"] ? "✓" : "✗") : ""}
              </li>
            ))}
          </ul>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-4 py-12" id="corpora">
        <h2 className="text-2xl font-bold">Four Wikipedia pages. One shared tokenizer.</h2>
        <p className="mt-2 text-sm text-[var(--color-ink)]/70">
          Frozen wiki-faithful Markdown snapshots — links, URLs, tables, references, punctuation and visible Markdown
          syntax remain in the evaluation input.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {LANG_ORDER.map((lang) => {
            const c = data.corpora[lang];
            const d = LANG_DISPLAY[lang];
            return (
              <div key={lang} className="rounded-lg border border-[var(--color-ink)]/10 p-4 text-sm">
                <div className={`font-semibold ${d.fontClass}`}>{d.native} — {c.article}</div>
                <div className="mt-2 font-mono text-xs break-all text-[var(--color-ink)]/60">{c.source_url}</div>
                <div className="mt-1 font-mono text-xs">{c.frozen_path}</div>
                <div className="mt-2">Faithful units: {c.faithful_units.toLocaleString()}</div>
                <div className="font-mono text-xs">SHA-256: {c.sha256.slice(0, 20)}…</div>
                <a className="mt-2 inline-block text-[var(--color-indigo)] underline" href={`/data/submission/corpus/${lang}.faithful.md`} download>
                  View frozen Markdown
                </a>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="faithfulness">
        <h2 className="text-2xl font-bold">Nothing visible gets lost</h2>
        <div className="mt-4 grid gap-4 font-mono text-xs md:grid-cols-2">
          <div><div className="font-sans text-sm font-semibold">INPUT</div>{rev.original_text}</div>
          <div><div className="font-sans text-sm font-semibold">DECODE</div>{rev.decoded_text}</div>
          <div className="md:col-span-2"><div className="font-sans text-sm font-semibold">FAITHFUL UNITS</div>{rev.faithful_units.join(" · ")}</div>
          <div className="md:col-span-2"><div className="font-sans text-sm font-semibold">ENCODE</div>{rev.bpe_tokens.join(" ")}</div>
          <div className="md:col-span-2"><div className="font-sans text-sm font-semibold">TOKEN IDs</div>{(rev.token_ids ?? []).join(", ")}</div>
          <div>VISIBLE ROUND-TRIP {badge(data.roundtrip.reviewer_sample)}</div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          {Object.entries(data.roundtrip.samples).map(([s, ok]) => (
            <span key={s} className="rounded border px-2 py-1">{s.slice(0, 24)}{s.length > 24 ? "…" : ""}: {ok ? "✓" : "✗"}</span>
          ))}
          {LANG_ORDER.map((l) => (
            <span key={l} className="rounded border px-2 py-1">Full {l.toUpperCase()}: {data.roundtrip.full_corpus[l] ? "✓" : "✗"}</span>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="fertility-explainer">
        <h2 className="text-2xl font-bold">How can fertility be below 1?</h2>
        <p className="mt-2 max-w-3xl text-sm text-[var(--color-ink)]/75">
          The evaluator uses faithful units: each letter/mark/number run is one unit; each visible punctuation or symbol
          is its own unit. A BPE token can span multiple faithful units, so token count can be lower than unit count.
        </p>
        <p className="mt-2 font-mono text-sm">
          Reviewer sample: {rev.faithful_unit_count} faithful units · {rev.bpe_token_count} BPE tokens · fertility{" "}
          {rev.fertility?.toFixed(4)}
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-2 text-xs">
          {LANG_ORDER.map((lang) => {
            const ex = data.fertilityExamples.per_language[lang];
            return (
              <div key={lang} className="rounded border p-3">
                <div className="font-semibold">{LANG_DISPLAY[lang].label}</div>
                <div className="mt-1 truncate">{ex.original_text}</div>
                <div className="mt-1">Units: {ex.faithful_unit_count} · Tokens: {ex.bpe_token_count} · Fertility: {ex.fertility?.toFixed(4)}</div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="result">
        <h2 className="text-2xl font-bold">Verified fertility</h2>
        <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
          {LANG_ORDER.map((lang) => {
            const d = LANG_DISPLAY[lang];
            const fu = m.faithful_unit_counts[lang];
            const tc = m.token_counts[lang];
            const fert = m.fertilities[lang];
            return (
              <div key={lang} className="text-center">
                <div className={`text-sm font-semibold ${d.fontClass}`}>{d.native}</div>
                <div className="mt-2 font-mono text-2xl font-bold">{fert.toFixed(4)}</div>
                <div className="mt-1 text-xs">{tc.toLocaleString()} / {fu.toLocaleString()} = {fert.toFixed(4)}</div>
                {(lang === "en" || lang === "hi") && (
                  <div className="mt-2">&lt; 1.2: {badge(data.thresholds[`${lang}_under_1_2` as "en_under_1_2" | "hi_under_1_2"])}</div>
                )}
              </div>
            );
          })}
        </div>
        <details className="mt-8 text-sm">
          <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">Scoring details</summary>
          <p className="mt-2 font-mono">Spread {m.spread.toFixed(6)} · Raw {m.raw_score.toFixed(2)} · Penalty {m.hindi_penalty.toFixed(4)}× · Adjusted {m.adjusted_score.toFixed(2)}</p>
        </details>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="vocabulary">
        <h2 className="text-2xl font-bold">Inside the shared 10K vocabulary</h2>
        <p className="mt-2 text-sm text-[var(--color-ink)]/70">
          Script composition by Unicode — not fixed per-language quotas. Weights change training exposure, not token
          ownership.
        </p>
        <div className="mt-4 space-y-1 text-sm font-mono">
          {Object.entries(comp.categories).map(([k, n]) => (
            <div key={k} className="flex justify-between border-b border-[var(--color-ink)]/8 py-1">
              <span>{CAT_LABELS[k] ?? k}</span>
              <span>{n} ({((100 * n) / comp.vocab_size).toFixed(1)}%)</span>
            </div>
          ))}
          <div className="flex justify-between py-1 font-bold"><span>Total</span><span>{comp.sum}</span></div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12" id="vocab-util">
        <h2 className="text-2xl font-bold">How the four corpora use the shared vocabulary</h2>
        <div className="mt-4 grid gap-2 text-sm font-mono md:grid-cols-2">
          {LANG_ORDER.map((l) => (
            <div key={l}>{l.toUpperCase()} unique token IDs: {util.per_corpus_unique_ids[l].toLocaleString()}</div>
          ))}
          <div>Used by ≥1 corpus: {util.used_by_at_least_one.toLocaleString()}</div>
          <div>Unused by all four: {util.unused_by_all_four.toLocaleString()}</div>
          <div>Used by exactly one: {util.used_by_exactly_one.toLocaleString()}</div>
          <div>Used by all four: {util.used_by_all_four.toLocaleString()}</div>
        </div>
        <p className="mt-3 text-xs text-[var(--color-ink)]/60">Counts overlap — four per-corpus counts do not sum to 10,000.</p>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16" id="innovation">
        <h2 className="text-2xl font-bold">Where SamaBPE adds intelligence</h2>
        <p className="mt-2 text-sm">Weights influence training exposure — not fixed per-language token quotas.</p>
        <p className="mt-4 font-mono text-sm">
          Baseline EN {opt.baseline_weights?.en} · HI {opt.baseline_weights?.hi} · TE {opt.baseline_weights?.te} · BN {opt.baseline_weights?.bn}
        </p>
        <p className="mt-1 font-mono text-sm">
          Winner EN {data.provenance.weights.en} · HI {data.provenance.weights.hi} · TE {data.provenance.weights.te} · BN {data.provenance.weights.bn}
        </p>
        <p className="mt-2 text-sm">{opt.total_measured?.toLocaleString()} faithful-architecture tokenizers measured · {opt.candidates_passing_both_thresholds?.toLocaleString()} pass both thresholds</p>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-8">
        <div className="flex flex-wrap gap-3">
          <a href="/data/submission/tokenizer.json" download className="btn">tokenizer.json</a>
          <a href="/data/submission/encoder.py" download className="btn">encoder.py</a>
          <a href="/data/submission/evaluate_tokenizer.py" download className="btn">evaluate_tokenizer.py</a>
          <a href="/data/verifiedSubmission.json" download className="btn">verifiedSubmission.json</a>
          <a href="https://github.com/sohamzycus/neural-truth-lab/tree/main/session2" target="_blank" rel="noreferrer" className="btn">GitHub</a>
        </div>
        <p className="mt-4 font-mono text-xs text-[var(--color-ink)]/50">SHA-256 {data.tokenizer.sha256.slice(0, 24)}… · generated {data.generated_at}</p>
      </section>
    </>
  );
}

export function SectionLegacyResearch() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <details className="text-sm text-[var(--color-ink)]/60">
        <summary className="cursor-pointer font-medium">Legacy research history — not part of faithful resubmission</summary>
        <p className="mt-2">
          Prior work used NFKC + punctuation-to-space normalization, Whitespace pretokenizer, word-ish denominator,
          and custom JSON BPE. That pipeline failed the reviewer round-trip gate and is not the current submission.
        </p>
      </details>
    </section>
  );
}
