import type { ResubmissionMetrics, ResubmissionExperiments, ResubmissionComparison } from "../types";
import { LANG_DISPLAY } from "../types";

const LANG_ORDER = ["en", "hi", "te", "bn"] as const;
const THRESHOLD = 1.2;

const TRUST_MARKERS = [
  "Standard Hugging Face BPE",
  "One shared 10K vocabulary",
  "English · Hindi · Telugu · Bengali",
  "Executable and reproducible",
];

const ARCH_STEPS = [
  "Wiki-faithful corpora",
  "SamaBPE adaptive weight search",
  "Standard Hugging Face BPE training",
  "One tokenizer.json",
  "Four-language evaluation",
];

function thresholdBadge(lang: "en" | "hi", fertility: number) {
  const pass = fertility <= THRESHOLD;
  return (
    <span
      className={`mt-2 inline-block rounded px-2 py-0.5 text-xs font-semibold ${
        pass ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-900"
      }`}
    >
      {pass ? "≤ 1.2 ✓" : "> 1.2"}
    </span>
  );
}

export function ResubmissionHero({
  metrics,
  experiments,
  comparison,
}: {
  metrics: ResubmissionMetrics | null;
  experiments: ResubmissionExperiments | null;
  comparison: ResubmissionComparison | null;
}) {
  if (!metrics) {
    return (
      <header className="px-4 py-16 text-center" id="result">
        <p className="text-[var(--color-ink)]/50">Loading evaluator-compatible results…</p>
      </header>
    );
  }

  const s = metrics.scoring;
  const adjusted = s.adjusted_score ?? s.final_grade;
  const prov = metrics.provenance;
  const totalMeasured = experiments?.total_measured ?? experiments?.experiments?.length;

  return (
    <>
      <header className="px-4 pb-4 pt-10 md:pt-12" id="challenge">
        <div className="mx-auto max-w-6xl">
          <h1 className="font-sans text-[clamp(3rem,8vw,6rem)] font-extrabold leading-none tracking-tight">
            SamaBPE
          </h1>
          <p className="mt-4 text-[clamp(1.5rem,3.5vw,2.25rem)] font-bold text-[var(--color-indigo)]">
            One standard BPE tokenizer. Four languages. 10,000 tokens.
          </p>
          <p className="mt-3 max-w-3xl text-base text-[var(--color-ink)]/75">
            Built with <strong>Hugging Face BPE</strong> and an adaptive multilingual weight search that
            trains real tokenizer candidates, measures them on the same faithful Wikipedia corpus, and lets
            evidence choose the winner.
          </p>
          <ul className="mt-6 flex flex-wrap gap-2">
            {TRUST_MARKERS.map((m) => (
              <li key={m} className="rounded-full border border-[var(--color-indigo)]/25 px-3 py-1 text-xs font-medium">
                {m}
              </li>
            ))}
          </ul>
        </div>
      </header>

      <section className="border-y border-[var(--color-ink)]/10 bg-[var(--color-indigo)]/[0.03] px-4 py-8">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-2 text-center text-xs font-medium text-[var(--color-ink)]/70 md:text-sm">
          {ARCH_STEPS.map((step, i) => (
            <span key={step} className="flex items-center gap-2">
              {i > 0 && <span className="text-[var(--color-ink)]/30">→</span>}
              <span>{step}</span>
            </span>
          ))}
        </div>
        <pre className="mx-auto mt-6 max-w-xl overflow-x-auto rounded-lg bg-[var(--color-ink)]/90 p-4 text-left font-mono text-xs text-white">
{`from tokenizers import Tokenizer

tokenizer = Tokenizer.from_file("tokenizer.json")
tokens = tokenizer.encode("भारत India বাংলা తెలుగు")`}
        </pre>
        <p className="mt-2 text-center text-xs text-[var(--color-ink)]/55">
          Standard. Executable. No custom decoder required.
        </p>
      </section>

      <section className="px-4 py-12 md:py-16" id="result">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-saffron)]">
            Verified result
          </p>
          <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-4">
            {LANG_ORDER.map((lang) => {
              const l = metrics.languages[lang];
              const d = LANG_DISPLAY[lang];
              return (
                <div key={lang} className="text-center">
                  <div className={`text-sm font-semibold ${d.fontClass}`}>{d.native}</div>
                  <div className="mt-2 font-mono text-[clamp(1.75rem,4vw,2.75rem)] font-bold tabular-nums">
                    {l.fertility.toFixed(4)}
                  </div>
                  <div className="mt-1 text-xs text-[var(--color-ink)]/55">fertility (tokens / word-ish)</div>
                  {(lang === "en" || lang === "hi") && thresholdBadge(lang, l.fertility)}
                </div>
              );
            })}
          </div>

          <div className="mt-10 grid gap-6 text-center sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-[var(--color-ink)]/10 p-4">
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Spread</p>
              <p className="font-mono text-xl font-semibold tabular-nums">{s.spread.toFixed(6)}</p>
            </div>
            <div className="rounded-lg border border-[var(--color-ink)]/10 p-4">
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Raw score</p>
              <p className="font-mono text-xl font-semibold tabular-nums">
                {s.raw_score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
            <div className="rounded-lg border border-[var(--color-ink)]/10 p-4">
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Hindi penalty</p>
              <p className="font-mono text-xl font-semibold tabular-nums">{s.hindi_penalty.toFixed(4)}×</p>
            </div>
            <div className="rounded-lg border border-[var(--color-ink)]/10 p-4">
              <p className="text-xs uppercase tracking-wider text-[var(--color-ink)]/50">Adjusted evaluator score</p>
              <p className="font-mono text-xl font-semibold tabular-nums">
                {adjusted.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
          </div>

          <details className="mx-auto mt-8 max-w-2xl text-sm">
            <summary className="cursor-pointer font-medium text-[var(--color-indigo)]">
              How is the evaluator score calculated?
            </summary>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-[var(--color-ink)]/75">
              <li>Fertility = tokens / word-ish units</li>
              <li>Raw score = 1000 / (X<sub>max</sub> − X<sub>min</sub>)</li>
              <li>Hindi penalty = exp(max(0, X<sub>hi</sub> / 1.2 − 1))</li>
              <li>Adjusted score = raw score / Hindi penalty</li>
            </ul>
          </details>

          {comparison?.rows && (
            <div className="mt-10 overflow-x-auto">
              <h3 className="text-lg font-semibold">Experiment comparison</h3>
              <table className="mt-3 w-full min-w-[40rem] text-left text-sm">
                <thead>
                  <tr className="border-b text-xs uppercase text-[var(--color-ink)]/50">
                    <th className="py-2">Candidate</th>
                    <th>EN</th>
                    <th>HI</th>
                    <th>TE</th>
                    <th>BN</th>
                    <th>Spread</th>
                    <th className="text-right">Adjusted score</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.rows.filter(Boolean).map((row) => (
                    <tr
                      key={row!.label}
                      className={`border-b border-[var(--color-ink)]/8 font-mono text-xs ${
                        row!.label === "Final submission" ? "bg-[var(--color-saffron)]/10 font-semibold" : ""
                      }`}
                    >
                      <td className="py-2">{row!.label}</td>
                      <td>{row!.fertilities.en.toFixed(4)}</td>
                      <td>{row!.fertilities.hi.toFixed(4)}</td>
                      <td>{row!.fertilities.te.toFixed(4)}</td>
                      <td>{row!.fertilities.bn.toFixed(4)}</td>
                      <td>{row!.spread.toFixed(4)}</td>
                      <td className="text-right tabular-nums">
                        {row!.adjusted_score.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                      </td>
                      <td>{row!.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href="/data/submission/tokenizer.json" download className="btn">
              Download tokenizer.json
            </a>
            <a href="/data/submission/encoder.py" download className="btn">
              encoder.py
            </a>
            <a href="/data/submission/evaluate_tokenizer.py" download className="btn">
              evaluator
            </a>
            <a href="/data/results/resubmission_experiments.json" download className="btn">
              experiment registry
            </a>
            <a
              href="https://github.com/sohamzycus/neural-truth-lab"
              target="_blank"
              rel="noreferrer"
              className="btn"
            >
              GitHub
            </a>
          </div>

          <p className="mx-auto mt-4 max-w-2xl text-center font-mono text-xs text-[var(--color-ink)]/45">
            Format: Hugging Face BPE · Vocabulary: {metrics.tokenizer.vocab_size} · SHA-256{" "}
            {metrics.tokenizer.sha256.slice(0, 16)}…
            {prov?.weights && (
              <span className="block mt-1">
                Winning weights EN {prov.weights.en} · HI {prov.weights.hi} · TE {prov.weights.te} · BN{" "}
                {prov.weights.bn}
                {prov.constraint_class && ` · Class ${prov.constraint_class}`}
              </span>
            )}
            {totalMeasured != null && (
              <span className="block mt-1">{totalMeasured} real tokenizer candidates measured</span>
            )}
          </p>
        </div>
      </section>
    </>
  );
}

export function SectionInnovation({
  metrics,
  experiments,
}: {
  metrics: ResubmissionMetrics | null;
  experiments: ResubmissionExperiments | null;
}) {
  const w = metrics?.provenance?.weights;
  const total = experiments?.total_measured ?? experiments?.experiments?.length;

  return (
    <section className="mx-auto max-w-6xl px-4 py-16" id="innovation">
      <h2 className="text-[clamp(2rem,4vw,3rem)] font-bold">What makes SamaBPE different?</h2>
      <p className="mt-3 max-w-3xl text-[var(--color-ink)]/80">
        The tokenizer itself is <strong>standard Hugging Face BPE</strong>. The experiment is in deciding how
        to spend training exposure across four languages.
      </p>
      <p className="mt-2 max-w-3xl text-sm text-[var(--color-ink)]/65">
        <strong>Hugging Face BPE</strong> = tokenizer engine · <strong>SamaBPE</strong> = intelligent
        multilingual training-weight search. Weights do not change at runtime — one static{" "}
        <code>tokenizer.json</code> encodes all four languages.
      </p>
      <ol className="mt-8 space-y-4 border-l-2 border-[var(--color-indigo)]/30 pl-6 text-sm">
        {[
          "Choose weights",
          "Train real 10K BPE",
          "Measure all four languages",
          "Check thresholds and score",
          "Adjust weights",
          "Train again",
          "Best measured candidate wins",
        ].map((step, i) => (
          <li key={step}>
            <span className="font-mono text-[var(--color-indigo)]">{String(i + 1).padStart(2, "0")}</span>{" "}
            {step}
          </li>
        ))}
      </ol>
      {w && (
        <p className="mt-6 font-mono text-sm">
          Winner weights: EN {w.en} · HI {w.hi} · TE {w.te} · BN {w.bn}
        </p>
      )}
      {total != null && (
        <p className="mt-2 text-sm text-[var(--color-ink)]/60">
          {total} real Hugging Face BPE candidates trained and measured.
        </p>
      )}
    </section>
  );
}

export function SectionLegacyNote() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-8">
      <details className="text-sm text-[var(--color-ink)]/60">
        <summary className="cursor-pointer font-medium">Legacy custom tokenizer (research history)</summary>
        <p className="mt-2">
          The original custom SamaBPE JSON tokenizer and plain-text Wikipedia corpora remain in the repository
          for research history. They are <strong>not</strong> the current Hugging Face BPE submission.
        </p>
      </details>
    </section>
  );
}
