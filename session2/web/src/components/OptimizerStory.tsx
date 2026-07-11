import type { Stats } from "../types";
import { LANG_DISPLAY } from "../types";

type Landscape = {
  x_max_language?: string;
  x_min_language?: string;
  languages?: Array<{
    language: string;
    encoded_tokens: number;
    word_units: number;
    x: number;
    is_x_max?: boolean;
    is_x_min?: boolean;
    distance_from_x_max?: number;
  }>;
};

type RoiCandidate = {
  status?: string;
  language_focus?: string;
  word?: string;
  article_frequency?: number;
  predicted_score_delta?: number;
  predicted_gap_delta?: number;
  vocabulary_slots_consumed?: number;
  current_tokenization?: string[];
  proposed_tokenization?: string[];
};

type RoiData = { candidates?: RoiCandidate[]; baseline?: { x_max_language?: string } };

type BottleneckData = {
  language?: string;
  top_100_overhead?: Array<{ word: string; fragmentation_overhead: number; tokenization: string[] }>;
};

type MovingTrace = Array<{
  iteration: number;
  status?: string;
  description?: string;
  score?: number;
  gap?: number;
  previous_score?: number;
  new_score?: number;
  x_max_language?: string;
  boundary_transition?: boolean;
  accepted?: boolean;
}>;

type Sensitivity = { baseline_score?: number; improved?: boolean; best_track_a_score?: number };

export function SectionBottleneck({
  stats,
  landscape,
  bottleneck,
}: {
  stats: Stats | null;
  landscape: Landscape | null;
  bottleneck: BottleneckData | null;
}) {
  if (!stats) return null;
  const xMaxLang = landscape?.x_max_language ?? stats.languages.reduce((a, b) => (a.fertility > b.fertility ? a : b)).lang;
  const xMax = stats.languages.find((l) => l.lang === xMaxLang)!;
  const d = LANG_DISPLAY[xMaxLang as keyof typeof LANG_DISPLAY];
  const top = bottleneck?.top_100_overhead?.[0];

  return (
    <section className="mx-auto max-w-6xl px-4 py-10" id="bottleneck">
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--color-saffron)]">Current bottleneck</p>
      <h2 className="mt-2 text-[clamp(1.75rem,3vw,2.5rem)] font-bold">What limits the score?</h2>
      <div className="mt-6 card border-l-4 border-[var(--color-saffron)]">
        <div className={`text-2xl font-bold ${d?.fontClass ?? ""}`}>{d?.native ?? xMax.label}</div>
        <div className="mt-2 font-mono text-4xl font-bold tabular-nums">{xMax.fertility.toFixed(4)}</div>
        <p className="mt-2 text-base text-[var(--color-ink)]/75">
          This language currently defines <strong>X_max</strong> and therefore limits the assignment score.
        </p>
        <dl className="mt-4 grid gap-2 font-mono text-sm md:grid-cols-3">
          <div><dt className="text-[var(--color-ink)]/50">Tokens</dt><dd>{xMax.tokens.toLocaleString()}</dd></div>
          <div><dt className="text-[var(--color-ink)]/50">Word units</dt><dd>{xMax.word_units.toLocaleString()}</dd></div>
          <div><dt className="text-[var(--color-ink)]/50">Distance from next</dt><dd>{xMax.distance_from_worst?.toFixed(4) ?? "—"}</dd></div>
        </dl>
        {top && (
          <p className="mt-4 text-sm text-[var(--color-ink)]/65">
            <span className="text-xs uppercase tracking-wide text-[var(--color-indigo)]">MEASURED</span> Top fragmentation source:{" "}
            <code className="font-mono">{top.word}</code> → {top.tokenization.map((t) => t.replace("</w>", "·")).join(" ")} (
            overhead {top.fragmentation_overhead})
          </p>
        )}
      </div>
    </section>
  );
}

export function SectionOptimizerNextMove({ roi }: { roi: RoiData | null }) {
  const predicted = roi?.candidates?.find((c) => c.status === "PREDICTED" && c.predicted_score_delta);
  const measured = roi?.candidates?.find((c) => c.status === "MEASURED");

  return (
    <section className="mx-auto max-w-6xl px-4 py-10" id="optimizer">
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--color-indigo)]">The optimizer&apos;s next move</p>
      <h2 className="mt-2 text-[clamp(1.75rem,3vw,2.5rem)] font-bold">
        If SamaBPE received one more vocabulary slot, where should it go?
      </h2>
      <p className="mt-3 max-w-3xl text-base text-[var(--color-ink)]/75">
        A frequent merge is not automatically a good merge. SamaBPE values a vocabulary decision by its effect on the
        global min–max fertility gap.
      </p>
      {predicted ? (
        <div className="mt-6 card">
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold uppercase text-amber-900">PREDICTED</span>
          <dl className="mt-3 space-y-2 font-mono text-sm">
            <div>Target: {predicted.language_focus} · candidate: {predicted.word}</div>
            <div>Frequency: {predicted.article_frequency} · slots: {predicted.vocabulary_slots_consumed ?? 1}</div>
            {predicted.predicted_score_delta != null && (
              <div>Predicted score Δ: +{predicted.predicted_score_delta.toFixed(2)}</div>
            )}
          </dl>
        </div>
      ) : measured ? (
        <div className="mt-6 card">
          <span className="rounded bg-[var(--color-indigo)]/15 px-2 py-0.5 text-xs font-semibold uppercase text-[var(--color-indigo)]">MEASURED</span>
          <p className="mt-3 text-sm">
            Highest-impact region: <strong>{measured.language_focus}</strong> corpus aggregate (gap above X_min:{" "}
            {(measured as { gap_above_x_min?: number }).gap_above_x_min?.toFixed(4) ?? "—"})
          </p>
          <p className="mt-2 text-xs text-[var(--color-ink)]/55">
            At 10K vocab, single-merge headroom is limited — bounded search tested bootstrap and weight reallocation.
          </p>
        </div>
      ) : (
        <p className="mt-4 text-sm text-[var(--color-ink)]/55">Run <code>python scripts/score_optimization.py</code> to generate ROI candidates.</p>
      )}
    </section>
  );
}

export function SectionMovingBoundary({ trace, sensitivity }: { trace: MovingTrace | null; sensitivity: Sensitivity | null }) {
  if (!trace?.length) return null;
  const improved = sensitivity?.improved;
  return (
    <section className="mx-auto max-w-6xl px-4 py-10" id="moving-boundary">
      <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--color-leaf)]">The moving boundary</p>
      <h2 className="mt-2 text-[clamp(1.75rem,3vw,2.5rem)] font-bold">Bounded optimization trace</h2>
      <p className="mt-2 text-sm text-[var(--color-ink)]/60">
        <span className="font-medium">MEASURED</span> — bootstrap sweep, representation comparison, local weight search
      </p>
      {improved === false && sensitivity?.baseline_score && (
        <p className="mt-3 text-base">
          Baseline <span className="font-mono font-semibold">{sensitivity.baseline_score.toFixed(2)}</span> retained — no verified improvement found.
        </p>
      )}
      <ol className="mt-6 space-y-4">
        {trace.map((step) => (
          <li key={step.iteration} className="card">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-[var(--color-ink)]/50">Iteration {step.iteration}</span>
              <span className="rounded bg-[var(--color-leaf)]/15 px-2 py-0.5 text-xs font-medium">{step.status ?? "VERIFIED"}</span>
            </div>
            <p className="mt-2 font-medium">{step.description}</p>
            <div className="mt-2 font-mono text-sm tabular-nums">
              Score: {step.previous_score != null ? `${step.previous_score.toFixed(2)} → ` : ""}
              {(step.new_score ?? step.score)?.toFixed(2)} · Gap: {step.gap?.toFixed(4)}
            </div>
            {step.boundary_transition && (
              <p className="mt-2 text-sm font-medium text-[var(--color-saffron)]">BOUNDARY SHIFT detected</p>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}

export function SectionTokenEconomyStory({
  stats,
  headroom,
}: {
  stats: Stats | null;
  headroom: { integer_token_headroom?: number; numeric_headroom?: number } | null;
}) {
  if (!stats) return null;
  const alloc = stats.vocab_attribution ?? stats.vocab_allocation ?? {};
  return (
    <section className="mx-auto max-w-6xl px-4 py-10" id="economy">
      <h2 className="text-[clamp(1.75rem,3vw,2.5rem)] font-bold">The 10,000-token economy</h2>
      <p className="mt-2 text-base text-[var(--color-ink)]/75">
        Every vocabulary slot is scarce. Giving one language more representation can change the global balance.
      </p>
      {headroom && (
        <p className="mt-3 text-sm">
          <span className="text-xs uppercase tracking-wide text-[var(--color-indigo)]">MEASURED</span> English headroom under X≤1.2:{" "}
          <span className="font-mono">{headroom.integer_token_headroom?.toLocaleString()}</span> tokens · numeric margin{" "}
          {headroom.numeric_headroom?.toFixed(4)}
        </p>
      )}
      <div className="mt-4 grid gap-2 font-mono text-xs md:grid-cols-3">
        {Object.entries(alloc).map(([k, v]) => (
          <div key={k} className="card flex justify-between">
            <span>{k}</span>
            <span className="tabular-nums">{v}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
