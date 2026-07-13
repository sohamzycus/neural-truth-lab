import { useState } from "react";
import type { VerifiedSubmission } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

const CAT_COLORS: Record<string, string> = {
  latin_dominant: "#4338ca",
  devanagari_dominant: "#ea580c",
  telugu_dominant: "#059669",
  bengali_dominant: "#db2777",
  shared_punctuation_digits_symbols: "#94a3b8",
  mixed_script: "#7c3aed",
  other_unicode: "#64748b",
  special_token: "#1e293b",
};

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

function fmt(n: number, d = 4) {
  return n.toLocaleString(undefined, { maximumFractionDigits: d });
}

function FertilityRange({ fertilities }: { fertilities: Record<string, number> }) {
  const entries = LANG_ORDER.map((l) => ({ lang: l, v: fertilities[l], label: LANG_DISPLAY[l].label }));
  const min = Math.min(...entries.map((e) => e.v)) - 0.005;
  const max = Math.max(...entries.map((e) => e.v)) + 0.005;
  const span = max - min || 1;
  const colors: Record<string, string> = { en: "#4338ca", hi: "#ea580c", te: "#059669", bn: "#db2777" };
  return (
    <div className="mt-8 rounded-lg border border-[var(--color-ink)]/10 p-6">
      <p className="text-sm text-[var(--color-ink)]/70">Four-language fertility range (tighter = better balance)</p>
      <div className="relative mt-6 h-12">
        <div className="absolute inset-x-0 top-1/2 h-0.5 -translate-y-1/2 bg-[var(--color-ink)]/15" />
        {entries.map((e) => (
          <div
            key={e.lang}
            className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${((e.v - min) / span) * 100}%` }}
            title={`${e.label}: ${e.v.toFixed(4)}`}
          >
            <div className="h-3 w-3 rounded-full" style={{ backgroundColor: colors[e.lang] }} />
            <div className="mt-2 whitespace-nowrap text-center text-[10px] font-mono">{e.label}</div>
          </div>
        ))}
      </div>
      <p className="mt-8 text-center font-mono text-xs">
        Spread = {(Math.max(...entries.map((e) => e.v)) - Math.min(...entries.map((e) => e.v))).toFixed(4)}
      </p>
    </div>
  );
}

function CorpusProvenance({ lang, c }: { lang: string; c: VerifiedSubmission["corpora"][string] }) {
  return (
    <details className="mt-2 text-xs text-[var(--color-ink)]/60">
      <summary className="cursor-pointer text-[var(--color-indigo)]">Technical provenance</summary>
      <ul className="mt-1 space-y-0.5 font-mono">
        <li>Path: {c.frozen_path}</li>
        {c.revision_id && <li>Revision: {c.revision_id}</li>}
        {c.fetch_timestamp && <li>Fetched: {c.fetch_timestamp}</li>}
        {c.builder_script && <li>Builder: {c.builder_script}</li>}
        <li>SHA-256: {c.sha256}</li>
      </ul>
    </details>
  );
}

function VocabMap({ data }: { data: VerifiedSubmission }) {
  const [hover, setHover] = useState<{ token: string; category: string } | null>(null);
  const entries = data.vocabularyMap ?? [];
  const comp = data.vocabularyComposition.categories;

  return (
    <div>
      <div
        className="mx-auto grid max-w-2xl gap-px rounded-lg border border-[var(--color-ink)]/10 p-1"
        style={{ gridTemplateColumns: "repeat(100, minmax(0, 1fr))" }}
        role="img"
        aria-label="10,000 vocabulary entries by script category"
      >
        {entries.map((e) => (
          <div
            key={e.id}
            className="aspect-square min-h-[3px] min-w-[3px] cursor-crosshair"
            style={{ backgroundColor: CAT_COLORS[e.category] ?? "#ccc" }}
            onMouseEnter={() => setHover({ token: e.token, category: e.category })}
            onMouseLeave={() => setHover(null)}
          />
        ))}
      </div>
      {hover && (
        <p className="mt-3 text-center font-mono text-xs">
          {CAT_LABELS[hover.category]} · <span className="text-[var(--color-indigo)]">{hover.token || "(empty)"}</span>
        </p>
      )}
      <div className="mt-4 flex flex-wrap justify-center gap-3 text-xs">
        {Object.entries(comp).map(([k, n]) => (
          <span key={k} className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: CAT_COLORS[k] }} />
            {CAT_LABELS[k]} ({n})
          </span>
        ))}
      </div>
    </div>
  );
}

export function ResearchStory({ data }: { data: VerifiedSubmission | null }) {
  if (!data) return <p className="p-12 text-center text-[var(--color-ink)]/50">Loading…</p>;

  const m = data.metrics;
  const opt = data.optimizer;
  const cmp = data.baselineVsWinner;
  const util = data.vocabularyUtilization;

  const evalUnits = (lang: string) =>
    m.evaluation_unit_counts?.[lang] ?? m.faithful_unit_counts[lang];

  return (
    <>
      {/* 1 HERO */}
      <header className="px-4 pb-8 pt-12 md:pt-16" id="overview">
        <div className="mx-auto max-w-6xl">
          <h1 className="font-sans text-[clamp(2.25rem,6vw,4.5rem)] font-extrabold leading-tight tracking-tight">
            How should four languages share just 10,000 tokens?
          </h1>
          <p className="mt-4 text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-[var(--color-indigo)]">SamaBPE finds out.</p>
          <p className="mt-4 max-w-3xl text-lg text-[var(--color-ink)]/80">
            English, Hindi, Telugu and Bengali compete for one shared BPE vocabulary. Hugging Face provides the
            tokenizer engine; SamaBPE searches multilingual training exposure to find a better balance across all four
            languages.
          </p>
          <ul className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
            {[
              ["4", "languages"],
              ["10,000", "shared vocabulary"],
              ["1", "Hugging Face BPE"],
              [data.experimentFunnel?.candidates_trained?.toLocaleString() ?? opt.total_measured?.toLocaleString() ?? "—", "candidates trained"],
            ].map(([n, l]) => (
              <li key={l} className="rounded-lg border border-[var(--color-indigo)]/15 p-4 text-center">
                <div className="font-mono text-2xl font-bold">{n}</div>
                <div className="text-xs text-[var(--color-ink)]/60">{l}</div>
              </li>
            ))}
          </ul>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#how-it-works" className="btn">See how SamaBPE works</a>
            <a href="#try-it" className="btn">Try the tokenizer</a>
            <a href="#reproduce" className="btn text-sm opacity-80">Reproduce locally</a>
          </div>
        </div>
      </header>

      {/* 2 CONSTRAINT */}
      <section className="border-y border-[var(--color-ink)]/10 bg-[var(--color-indigo)]/[0.03] px-4 py-14" id="constraint">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold">Four languages. One shared vocabulary.</h2>
          <p className="mt-2 text-[var(--color-ink)]/75">
            The same 10,000-token vocabulary must represent India&apos;s Wikipedia page in English, Hindi, Telugu and
            Bengali. One tokenizer. One vocabulary. No per-language model. No runtime language routing.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            {LANG_ORDER.map((lang) => {
              const c = data.corpora[lang];
              const d = LANG_DISPLAY[lang];
              return (
                <article key={lang} className="rounded-lg border border-[var(--color-ink)]/10 bg-white/50 p-4">
                  <div className={`text-lg font-semibold ${d.fontClass}`}>{d.native}</div>
                  <div className="text-sm">{c.article}</div>
                  <div className="mt-2 text-xs text-[var(--color-ink)]/60">
                    {c.characters.toLocaleString()} chars · {evalUnits(lang).toLocaleString()} evaluation units
                  </div>
                  <a href={c.source_url} target="_blank" rel="noreferrer" className="mt-2 block text-xs text-[var(--color-indigo)] underline">
                    Wikipedia source
                  </a>
                  <a href={`/data/submission/corpus/${lang}.faithful.md`} download className="mt-1 block text-xs text-[var(--color-indigo)]">
                    View frozen snapshot
                  </a>
                  <CorpusProvenance lang={lang} c={c} />
                </article>
              );
            })}
          </div>
        </div>
      </section>

      {/* 3 INNOVATION */}
      <section className="mx-auto max-w-6xl px-4 py-16" id="how-it-works">
        <h2 className="text-3xl font-bold">Hugging Face trains the tokenizer. SamaBPE decides how the languages compete.</h2>
        <p className="mt-4 max-w-3xl text-[var(--color-ink)]/80">
          A standard BPE tokenizer learns from the corpus exposure it receives. English, Hindi, Telugu and Bengali use
          very different scripts, and all four compete for only 10,000 shared vocabulary slots. SamaBPE systematically
          changes their relative training exposure, trains real Hugging Face BPE candidates, evaluates every valid
          candidate on the same four frozen Wikipedia snapshots, and keeps the strongest multilingual balance.
        </p>
        <p className="mt-3 text-sm text-[var(--color-ink)]/65">
          SamaBPE does not replace or modify Hugging Face BPE. It optimizes the multilingual training exposure given to
          the standard BPE trainer. Training weights influence which characters, subwords and merges compete for space
          in the shared vocabulary. They do not reserve fixed token quotas for each language.
        </p>
        <pre className="mt-6 overflow-x-auto rounded-lg bg-[var(--color-ink)]/90 p-4 text-xs text-white">
{`EN · HI · TE · BN — frozen Wikipedia snapshots
        ↓
Choose language exposure weights
        ↓
Train a real Hugging Face BPE tokenizer
        ↓
Validate lossless encode → decode
        ↓
Measure all four languages
        ↓
Compare multilingual balance
        ↓
Adjust weights and repeat
        ↓
Best measured valid candidate wins`}
        </pre>
      </section>

      {/* 4 SEARCH JOURNEY */}
      <section className="mx-auto max-w-6xl px-4 py-14">
        <h2 className="text-2xl font-bold">From baseline to SamaBPE winner</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border p-4">
            <div className="text-xs uppercase text-[var(--color-ink)]/50">Baseline weights</div>
            <div className="mt-1 font-mono text-lg">
              EN {data.baseline?.weights.en ?? opt.baseline_weights?.en} · HI {data.baseline?.weights.hi ?? opt.baseline_weights?.hi} · TE{" "}
              {data.baseline?.weights.te ?? opt.baseline_weights?.te} · BN {data.baseline?.weights.bn ?? opt.baseline_weights?.bn}
            </div>
          </div>
          <div className="rounded-lg border border-[var(--color-saffron)]/40 bg-[var(--color-saffron)]/5 p-4">
            <div className="text-xs uppercase text-[var(--color-ink)]/50">Winner weights</div>
            <div className="mt-1 font-mono text-lg font-semibold">
              EN {data.provenance.weights.en} · HI {data.provenance.weights.hi} · TE {data.provenance.weights.te} · BN{" "}
              {data.provenance.weights.bn}
            </div>
          </div>
        </div>
        {data.experimentFunnel && (
          <pre className="mt-6 overflow-x-auto rounded-lg border border-[var(--color-ink)]/10 bg-white/40 p-4 text-xs">
{`${data.experimentFunnel.candidates_trained} candidates trained
        ↓
${data.experimentFunnel.passed_roundtrip} passed lossless round-trip
        ↓
${data.experimentFunnel.passed_both_thresholds} passed EN & HI < 1.2
        ↓
${data.experimentFunnel.winner_count} winner`}
          </pre>
        )}
      </section>

      {/* 5 MONEY SHOT */}
      {cmp && data.baseline && (
        <section className="mx-auto max-w-6xl px-4 py-14" id="comparison">
          <h2 className="text-3xl font-bold">What did SamaBPE actually improve?</h2>
          <FertilityRange fertilities={m.fertilities} />
          <p className="mt-4 text-sm text-[var(--color-ink)]/75">
            SamaBPE reduced the gap between the best- and worst-performing languages from{" "}
            {(cmp.spread as { baseline: number }).baseline.toFixed(4)} to{" "}
            {(cmp.spread as { winner: number }).winner.toFixed(4)}, while keeping English and Hindi below 1.2.
          </p>
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[36rem] text-left text-sm">
              <thead>
                <tr className="border-b text-xs uppercase text-[var(--color-ink)]/50">
                  <th className="py-2">Metric</th>
                  <th>Baseline HF BPE</th>
                  <th>SamaBPE winner</th>
                  <th>Change</th>
                </tr>
              </thead>
              <tbody className="font-mono">
                {LANG_ORDER.map((lang) => {
                  const row = cmp[lang] as { baseline_fertility: number; winner_fertility: number; change: number };
                  return (
                    <tr key={lang} className="border-b border-[var(--color-ink)]/8">
                      <td className="py-2 font-sans">{LANG_DISPLAY[lang].label} fertility</td>
                      <td>{row.baseline_fertility.toFixed(4)}</td>
                      <td>{row.winner_fertility.toFixed(4)}</td>
                      <td className={row.change > 0 ? "text-amber-700" : "text-emerald-700"}>
                        {row.change > 0 ? "+" : ""}{row.change.toFixed(4)}
                      </td>
                    </tr>
                  );
                })}
                <tr className="border-b border-[var(--color-ink)]/8">
                  <td className="py-2 font-sans">Spread</td>
                  <td>{(cmp.spread as { baseline: number }).baseline.toFixed(4)}</td>
                  <td>{(cmp.spread as { winner: number }).winner.toFixed(4)}</td>
                  <td className="text-emerald-700">{(cmp.spread as { change: number }).change.toFixed(4)}</td>
                </tr>
                <tr>
                  <td className="py-2 font-sans">Calculated self-score</td>
                  <td>{(cmp.adjusted_score as { baseline: number }).baseline.toFixed(2)}</td>
                  <td>{(cmp.adjusted_score as { winner: number }).winner.toFixed(2)}</td>
                  <td className="text-emerald-700">+{((cmp.adjusted_score as { change: number }).change).toFixed(2)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* 6 VOCAB MAP */}
      <section className="mx-auto max-w-6xl px-4 py-16" id="vocabulary">
        <h2 className="text-3xl font-bold">What actually lives inside 10,000 shared tokens?</h2>
        <p className="mt-2 text-sm text-[var(--color-ink)]/70">
          Script composition is not language ownership. Latin tokens appear in URLs across corpora; digits and punctuation
          are naturally shared.
        </p>
        <div className="mt-8">
          <VocabMap data={data} />
        </div>
      </section>

      {data.vocabularyShift && (
        <section className="mx-auto max-w-6xl px-4 py-14">
          <h2 className="text-2xl font-bold">How did SamaBPE change the learned vocabulary?</h2>
          <p className="mt-2 text-sm text-[var(--color-ink)]/70">
            Comparing script composition of the baseline tokenizer (EN 3·HI 4·TE 4·BN 2) vs the winner.
          </p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[32rem] text-left text-sm">
              <thead>
                <tr className="border-b text-xs uppercase text-[var(--color-ink)]/50">
                  <th className="py-2">Category</th>
                  <th>Baseline</th>
                  <th>Winner</th>
                  <th>Delta</th>
                </tr>
              </thead>
              <tbody className="font-mono text-xs">
                {Object.entries(data.vocabularyShift.categories)
                  .filter(([k]) => k !== "mixed_other_combined")
                  .map(([k, row]) => {
                    const r = row as { baseline: number; winner: number; delta: number };
                    return (
                      <tr key={k} className="border-b border-[var(--color-ink)]/8">
                        <td className="py-2 font-sans">{CAT_LABELS[k] ?? k}</td>
                        <td>{r.baseline}</td>
                        <td>{r.winner}</td>
                        <td className={r.delta >= 0 ? "text-indigo-700" : "text-amber-700"}>{r.delta >= 0 ? "+" : ""}{r.delta}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* 7 UTILIZATION */}
      <section className="mx-auto max-w-6xl px-4 py-14" id="vocab-usage">
        <h2 className="text-2xl font-bold">One vocabulary, four different usage patterns</h2>
        <div className="mt-4 grid gap-2 font-mono text-sm md:grid-cols-2">
          {LANG_ORDER.map((l) => (
            <div key={l}>{l.toUpperCase()} unique token IDs: {util.per_corpus_unique_ids[l].toLocaleString()}</div>
          ))}
          <div>Used by ≥1 corpus: {util.used_by_at_least_one.toLocaleString()}</div>
          <div>Unused by all four: {util.unused_by_all_four.toLocaleString()}</div>
          <div>Used by exactly one: {util.used_by_exactly_one.toLocaleString()}</div>
          <div>Used by all four: {util.used_by_all_four.toLocaleString()}</div>
        </div>
        <p className="mt-3 text-xs text-[var(--color-ink)]/60">Sets overlap — four usage counts do not sum to 10,000.</p>
      </section>

      {/* 8 RESULTS */}
      <section className="mx-auto max-w-6xl px-4 py-16" id="results">
        <h2 className="text-3xl font-bold">The final measured result</h2>
        <div className="mt-8 grid grid-cols-2 gap-6 md:grid-cols-4">
          {LANG_ORDER.map((lang) => {
            const d = LANG_DISPLAY[lang];
            const fert = m.fertilities[lang];
            return (
              <div key={lang} className="rounded-lg border p-4 text-center">
                <div className={`font-semibold ${d.fontClass}`}>{d.native}</div>
                <div className="mt-2 font-mono text-xl font-bold">{fert.toFixed(4)}</div>
                <div className="mt-1 text-xs">
                  {m.token_counts[lang].toLocaleString()} tokens ÷ {evalUnits(lang).toLocaleString()} units
                  <details className="mt-1 text-left">
                    <summary className="cursor-pointer text-[var(--color-indigo)]">What does fertility mean?</summary>
                    <p className="mt-1 text-[var(--color-ink)]/65">
                      Encoded tokens divided by evaluation units. A BPE token can span multiple units, so fertility can
                      be below 1.
                    </p>
                  </details>
                </div>
                {(lang === "en" || lang === "hi") && (
                  <div className="mt-2 text-xs">&lt; 1.2: {data.thresholds[`${lang}_under_1_2` as "en_under_1_2"] ? "PASS" : "FAIL"}</div>
                )}
              </div>
            );
          })}
        </div>
        <p className="mt-6 font-mono text-sm">
          Spread {fmt(m.spread, 6)} · Hindi penalty {fmt(m.hindi_penalty, 4)}× · Calculated self-score {fmt(m.adjusted_score, 2)}
        </p>
        <details className="mt-4 text-sm">
          <summary className="cursor-pointer text-[var(--color-indigo)]">How is this calculated?</summary>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-[var(--color-ink)]/75">
            <li>Evaluation unit = contiguous letter/mark/number run or single visible symbol (wiki-faithful Markdown denominator)</li>
            <li>Fertility = encoded tokens ÷ evaluation units</li>
            <li>Spread = max fertility − min fertility across EN/HI/TE/BN</li>
            <li>Score = 1000 ÷ spread (÷ Hindi penalty if HI &gt; 1.2)</li>
          </ul>
        </details>
      </section>

      {/* 11 DOWNLOADS */}
      <section className="mx-auto max-w-6xl px-4 py-12" id="downloads">
        <h2 className="text-xl font-bold">Downloads & evidence</h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {[
            ["/data/submission/tokenizer.json", "tokenizer.json"],
            ["/data/submission/encoder.py", "encoder.py"],
            ["/data/submission/evaluate_tokenizer.py", "evaluate_tokenizer.py"],
            ["/data/submission/train_tokenizer.py", "train_tokenizer.py"],
            ["/data/verifiedSubmission.json", "verified data"],
            ["/data/results/resubmission_experiments.json", "experiments"],
            ["https://github.com/sohamzycus/neural-truth-lab/tree/main/session2", "GitHub"],
          ].map(([href, label]) => (
            <a key={label} href={href} download={href.startsWith("/") ? true : undefined} target={href.startsWith("http") ? "_blank" : undefined} rel="noreferrer" className="btn text-xs">
              {label}
            </a>
          ))}
        </div>
        <p className="mt-3 font-mono text-xs text-[var(--color-ink)]/50">
          HF BPE · NFKC · Metaspace · vocab {data.tokenizer.vocab_size} · SHA {data.tokenizer.sha256.slice(0, 20)}…
        </p>
      </section>

      {/* 12 METHODOLOGY */}
      <section className="mx-auto max-w-6xl px-4 py-12" id="methodology">
        <details className="text-sm">
          <summary className="cursor-pointer font-semibold">Methodology & technical details</summary>
          <div className="mt-4 space-y-2 text-[var(--color-ink)]/75">
            <p>Visible-text preservation: decode(encode(text)) keeps non-whitespace characters (NFKC-normalized for full corpora).</p>
            <p>Corpus hashes: {LANG_ORDER.map((l) => `${l.toUpperCase()} ${data.corpora[l].sha256.slice(0, 12)}…`).join(" · ")}</p>
            <p>Round-trip: reviewer sample {data.roundtrip.reviewer_sample ? "PASS" : "FAIL"} · full corpora{" "}
              {LANG_ORDER.map((l) => `${l.toUpperCase()} ${data.roundtrip.full_corpus[l] ? "✓" : "✗"}`).join(" ")}</p>
          </div>
        </details>
      </section>
    </>
  );
}

export function SectionReproduce({ data }: { data: VerifiedSubmission | null }) {
  if (!data) return null;
  const m = data.metrics;
  return (
    <section className="mx-auto max-w-6xl px-4 py-16" id="reproduce">
      <h2 className="text-3xl font-bold">Reproduce SamaBPE in 3 steps</h2>
      <ol className="mt-8 space-y-8">
        <li>
          <h3 className="font-semibold">1 — Get the exact corpus</h3>
          <p className="text-sm text-[var(--color-ink)]/70">English · Hindi · Telugu · Bengali — India Wikipedia snapshots</p>
          <a href="/data/submission/corpus/en.faithful.md" download className="btn mt-2 text-xs">Download corpus</a>
        </li>
        <li>
          <h3 className="font-semibold">2 — Load the exact tokenizer</h3>
          <pre className="mt-2 overflow-x-auto rounded bg-[var(--color-ink)]/90 p-3 text-xs text-white">{`from tokenizers import Tokenizer\ntokenizer = Tokenizer.from_file("tokenizer.json")`}</pre>
          <a href="/data/submission/tokenizer.json" download className="btn mt-2 text-xs">Download tokenizer.json</a>
        </li>
        <li>
          <h3 className="font-semibold">3 — Run the evaluation</h3>
          <pre className="mt-2 overflow-x-auto rounded bg-[var(--color-ink)]/90 p-3 text-xs text-white">{`cd submission\npip install -r requirements.txt\npython evaluate_tokenizer.py`}</pre>
          <p className="mt-2 font-mono text-xs text-[var(--color-ink)]/60">
            EN {m.fertilities.en.toFixed(4)} · HI {m.fertilities.hi.toFixed(4)} · TE {m.fertilities.te.toFixed(4)} · BN{" "}
            {m.fertilities.bn.toFixed(4)} · Spread {m.spread.toFixed(4)} · Score {m.adjusted_score.toFixed(2)}
          </p>
        </li>
      </ol>
    </section>
  );
}

export function SectionTryIt({
  encoder,
  playText,
  setPlayText,
}: {
  encoder: import("../lib/hf-encoder").HfBpeEncoder | null;
  playText: string;
  setPlayText: (t: string) => void;
}) {
  const DEFAULT = `India's population is 1,428,627,663.
भारत एक विशाल देश है।
భారతదేశం వైవిధ్యభరితమైన దేశం.
ভারত একটি বৈচিত্র্যময় দেশ।`;

  const presets = [
    ["English + punctuation", "India's population is 1,428,627,663."],
    ["Hindi", "भारत एक विविध देश है।"],
    ["Telugu", "భారతదేశం వైవిధ్యభరితమైన దేశం."],
    ["Bengali", "ভারত একটি বৈচিত্র্যময় দেশ।"],
    ["Mixed script", "India भारत తెలుగు বাংলা"],
    ["Markdown URL", "[India](https://en.wikipedia.org/wiki/India)"],
  ] as const;

  const tokens = encoder ? encoder.encodeTokens(playText) : [];
  const ids = encoder ? encoder.encodeIds(playText) : [];
  const decoded = encoder ? encoder.decode(ids) : "";
  const rtOk = encoder ? encoder.verifyRoundtrip(playText) : false;

  return (
    <section className="mx-auto max-w-6xl px-4 py-16" id="try-it">
      <h2 className="text-3xl font-bold">Test the exact submitted tokenizer</h2>
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" className="btn text-xs" onClick={() => setPlayText(DEFAULT)}>Load multilingual sample</button>
        {presets.map(([label, text]) => (
          <button key={label} type="button" className="btn text-xs" onClick={() => setPlayText(text)}>{label}</button>
        ))}
      </div>
      <textarea
        className="mt-4 w-full rounded border border-[var(--color-ink)]/15 bg-white/40 p-4 font-mono text-sm"
        rows={5}
        value={playText}
        onChange={(e) => setPlayText(e.target.value)}
        aria-label="Tokenizer input"
      />
      {encoder && (
        <div className="mt-4 space-y-3 font-mono text-xs">
          <div><span className="font-sans font-semibold">Tokens ({tokens.length}):</span> {tokens.join(" ")}</div>
          <div><span className="font-sans font-semibold">IDs:</span> {ids.join(", ")}</div>
          <div><span className="font-sans font-semibold">Decoded:</span> {decoded}</div>
          <div><span className="font-sans font-semibold">Visible-text preservation:</span> {rtOk ? "PASS" : "FAIL"}</div>
        </div>
      )}
    </section>
  );
}
