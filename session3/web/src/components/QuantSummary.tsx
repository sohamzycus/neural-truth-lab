import type { DataMix, LanguageWeights } from "../types";

export function QuantSummary({
  lang,
  mix,
}: {
  lang: LanguageWeights | null;
  mix: DataMix | null;
}) {
  if (!lang || !mix) return null;

  const topLangs = Object.entries(lang.weights_percent)
    .sort(([, a], [, b]) => Number(b) - Number(a))
    .slice(0, 6);

  return (
    <section className="grid gap-4 md:grid-cols-2">
      <div className="rounded border border-[var(--border)] bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
          Pretrain Slices (1.2T)
        </h3>
        <ul className="space-y-1 text-sm">
          {Object.entries(mix.slice_tokens_billions).map(([k, v]) => (
            <li key={k} className="flex justify-between">
              <span>{k.replace(/_/g, " ")}</span>
              <span className="font-medium tabular-nums">{v}B</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="rounded border border-[var(--border)] bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
          MCDA Language Weights (top 6)
        </h3>
        <ul className="space-y-1 text-sm">
          {topLangs.map(([k, v]) => (
            <li key={k} className="flex justify-between">
              <span>{k}</span>
              <span className="font-medium tabular-nums">{v}%</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-[var(--muted)]">
          Hindi MCDA {lang.hindi_mcda_vs_population.mcda_percent}% vs population{" "}
          {lang.hindi_mcda_vs_population.population_percent}% (
          {lang.hindi_mcda_vs_population.delta_pp}pp)
        </p>
      </div>
    </section>
  );
}
