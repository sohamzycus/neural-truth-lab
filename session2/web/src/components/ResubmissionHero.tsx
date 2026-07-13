import type { ResubmissionMetrics, ResubmissionExperiments } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;

export function ResubmissionHero({
  metrics,
  experiments,
}: {
  metrics: ResubmissionMetrics | null;
  experiments: ResubmissionExperiments | null;
}) {
  if (!metrics) {
    return (
      <header className="px-4 py-16 text-center" id="result">
        <p className="text-[var(--color-ink)]/50">Loading evaluator-compatible results…</p>
      </header>
    );
  }

  const s = metrics.scoring;
  const prov = metrics.provenance;

  return (
    <>
      <header className="px-4 pb-6 pt-10 md:pt-12" id="challenge">
        <div className="mx-auto max-w-6xl">
          <h1 className="font-sans text-[clamp(3rem,8vw,6rem)] font-extrabold leading-none tracking-tight">
            SamaBPE
          </h1>
          <p className="mt-4 text-[clamp(1.75rem,4vw,2.75rem)] font-bold text-[var(--color-indigo)]">
            Standard Hugging Face BPE · adaptive weight search
          </p>
          <p className="mt-3 max-w-3xl text-base text-[var(--color-ink)]/75">
            One shared tokenizer (≤10K). Wiki-faithful Markdown corpora. Optimized for the actual final
            grade — not raw score alone.
          </p>
        </div>
      </header>

      <section className="border-y border-[var(--color-ink)]/10 px-4 py-12 md:py-16" id="result">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-saffron)]">
            Evaluator-compatible result · VERIFIED
          </p>
          <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-4">
            {LANG_ORDER.map((lang) => {
              const l = metrics.languages[lang];
              const d = LANG_DISPLAY[lang];
              return (
                <div key={lang} className="text-center">
                  <div className={`text-sm font-semibold ${d.fontClass}`}>{d.native}</div>
                  <div className="mt-2 font-mono text-[clamp(2rem,4.5vw,3rem)] font-bold tabular-nums">
                    {l.fertility.toFixed(6)}
                  </div>
                  <div className="mt-1 text-xs text-[var(--color-ink)]/55">tokens / word-ish unit</div>
                  <div className="mt-1 font-mono text-xs tabular-nums text-[var(--color-ink)]/45">
                    {l.tokens.toLocaleString()} ÷ {l.wordish_units.toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-12 grid gap-8 text-center md:grid-cols-3">
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Raw score</p>
              <p className="font-mono text-[clamp(2rem,5vw,3.5rem)] font-bold tabular-nums">
                {s.raw_score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-[var(--color-ink)]/50">1000 ÷ {s.spread.toFixed(6)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Hindi penalty</p>
              <p className="font-mono text-[clamp(2rem,5vw,3.5rem)] font-bold tabular-nums">
                {s.hindi_penalty.toFixed(4)}×
              </p>
              <p className="text-xs text-[var(--color-ink)]/50">exp(max(0, X<sub>hi</sub>/1.2 − 1))</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-[var(--color-saffron)]">Final grade</p>
              <p className="font-mono text-[clamp(3.5rem,9vw,7rem)] font-extrabold leading-none tabular-nums">
                {s.final_grade.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          <details className="mx-auto mt-8 max-w-2xl text-sm">
            <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">
              How is the final grade calculated?
            </summary>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-[var(--color-ink)]/75">
              <li>Raw score = 1000 / (X<sub>max</sub> − X<sub>min</sub>)</li>
              <li>Hindi penalty = exp(max(0, X<sub>hi</sub> / 1.2 − 1))</li>
              <li>Final grade = Raw score / Hindi penalty</li>
            </ul>
            <p className="mt-2 text-[var(--color-ink)]/65">
              SamaBPE optimizes the actual final grade — a smaller spread helps, but Hindi above 1.2 adds an
              exponential penalty.
            </p>
          </details>

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href="/data/submission/tokenizer.json" download className="btn">
              Download tokenizer.json
            </a>
            <a href="/data/submission/encoder.py" download className="btn">
              encoder.py
            </a>
            <a href="/data/submission/metrics.json" download className="btn">
              metrics.json
            </a>
            <a href="#weight-search" className="btn">
              How SamaBPE searches
            </a>
            <a href="#reproduce" className="btn">
              Reproduce
            </a>
          </div>

          <div className="mt-10 border-t border-[var(--color-ink)]/10 pt-8" id="corpus">
            <h3 className="text-lg font-semibold">Evaluation corpus</h3>
            <p className="mt-2 text-sm text-[var(--color-ink)]/70">
              Wiki-faithful Markdown snapshots of India&apos;s Wikipedia page in English, Hindi, Telugu, and
              Bengali. Links, URLs, tables, references, image links, navboxes, and categories are preserved
              where emitted by HTML-to-Markdown conversion.
            </p>
            {metrics.corpus_sha256 && (
              <dl className="mt-4 grid gap-2 font-mono text-xs sm:grid-cols-2">
                {LANG_ORDER.map((lang) => {
                  const l = metrics.languages[lang];
                  const sha = metrics.corpus_sha256?.[lang];
                  const d = LANG_DISPLAY[lang];
                  return (
                    <div key={lang} className="rounded border border-[var(--color-ink)]/10 p-2">
                      <dt className={d.fontClass}>{d.native}</dt>
                      <dd className="mt-1 text-[var(--color-ink)]/60">
                        {l.wordish_units.toLocaleString()} word-ish units
                      </dd>
                      {sha && <dd className="truncate text-[var(--color-ink)]/45">SHA {sha.slice(0, 20)}…</dd>}
                    </div>
                  );
                })}
              </dl>
            )}
          </div>
          <p className="mx-auto mt-4 max-w-xl text-center font-mono text-xs text-[var(--color-ink)]/45">
            HF BPE · vocab {metrics.tokenizer.vocab_size} · SHA-256 {metrics.tokenizer.sha256.slice(0, 16)}…
            {prov?.weights && (
              <span className="block mt-1">
                Weights EN {prov.weights.en} · HI {prov.weights.hi} · TE {prov.weights.te} · BN{" "}
                {prov.weights.bn}
              </span>
            )}
          </p>
        </div>
      </section>
    </>
  );
}

export function SectionWeightSearch({ experiments }: { experiments: ResubmissionExperiments | null }) {
  if (!experiments?.experiments?.length) return null;
  const sorted = [...experiments.experiments].sort((a, b) => b.final_grade - a.final_grade);
  const show = [sorted[sorted.length - 1], sorted[Math.floor(sorted.length / 2)], sorted[1], sorted[0]].filter(
    Boolean,
  );
  const seen = new Set<string>();
  const picks = show.filter((e) => {
    const k = e.experiment_id;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });

  return (
    <section className="mx-auto max-w-6xl px-4 py-16" id="weight-search">
      <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">How SamaBPE searches</h2>
      <p className="mt-3 max-w-3xl text-[var(--color-ink)]/80">
        SamaBPE innovates in <strong>training-time</strong> multilingual weight search. Each candidate is a
        real standard Hugging Face BPE tokenizer — no runtime language routing.
      </p>
      <ol className="mt-8 space-y-6 border-l-2 border-[var(--color-indigo)]/30 pl-6">
        {[
          "Choose multilingual training weights",
          "Train a real standard Hugging Face BPE",
          "Evaluate all four faithful Wikipedia corpora",
          "Calculate raw score + Hindi penalty + final grade",
          "SamaBPE proposes the next weight configuration",
          "Best measured candidate wins",
        ].map((step, i) => (
          <li key={step} className="text-sm">
            <span className="font-mono text-[var(--color-indigo)]">{String(i + 1).padStart(2, "0")}</span>{" "}
            {step}
          </li>
        ))}
      </ol>
      <div className="mt-10 overflow-x-auto">
        <table className="w-full min-w-[32rem] text-left text-sm">
          <thead>
            <tr className="border-b text-xs uppercase text-[var(--color-ink)]/50">
              <th className="py-2">Experiment</th>
              <th>Weights</th>
              <th className="text-right">Final grade</th>
            </tr>
          </thead>
          <tbody>
            {picks.map((e) => (
              <tr key={e.experiment_id} className="border-b border-[var(--color-ink)]/8 font-mono text-xs">
                <td className="py-2">{e.experiment_id}</td>
                <td>
                  EN {e.weights.en} · HI {e.weights.hi} · TE {e.weights.te} · BN {e.weights.bn}
                </td>
                <td className="text-right tabular-nums font-semibold">{e.final_grade.toFixed(2)}</td>
              </tr>
            ))}
            {sorted[0] && (
              <tr className="bg-[var(--color-saffron)]/10 font-semibold">
                <td className="py-2">WINNER</td>
                <td>
                  EN {sorted[0].weights.en} · HI {sorted[0].weights.hi} · TE {sorted[0].weights.te} · BN{" "}
                  {sorted[0].weights.bn}
                </td>
                <td className="text-right tabular-nums">{sorted[0].final_grade.toFixed(2)}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function SectionLegacyNote() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <details className="text-sm text-[var(--color-ink)]/60">
        <summary className="cursor-pointer font-medium">Legacy internal experiment (not resubmission)</summary>
        <p className="mt-2">
          The original custom SamaBPE JSON tokenizer and plain-text Wikipedia corpora remain in the repository
          for research history. They are not the evaluator-compatible resubmission result.
        </p>
      </details>
    </section>
  );
}
