import type { LanguageWeights } from "../types";

const LANG_LABELS: Record<string, string> = {
  hi: "Hindi",
  en_in: "English-IN",
  bn: "Bengali",
  te: "Telugu",
  ta: "Tamil",
  mr: "Marathi",
  gu: "Gujarati",
  kn: "Kannada",
};

export function LanguageMixCompare({ lang }: { lang: LanguageWeights | null }) {
  if (!lang) return null;

  const entries = Object.keys(LANG_LABELS)
    .map((k) => ({
      key: k,
      label: LANG_LABELS[k],
      mcda: Number(lang.weights_percent[k]),
      pop: lang.population_baseline_percent[k],
    }))
    .sort((a, b) => b.mcda - a.mcda);

  const max = Math.max(...entries.flatMap((e) => [e.mcda, e.pop]));

  return (
    <section className="rounded border border-[var(--border)] bg-white p-5">
      <h3 className="font-semibold">MCDA vs Population Weighting</h3>
      <p className="mt-1 text-sm text-[var(--muted)]">
        Why Hindi drops from {lang.population_baseline_percent.hi}% (census) to{" "}
        {lang.weights_percent.hi}% (MCDA) — and Dravidian languages gain{" "}
        {(lang.dravidian_collective_mcda - lang.dravidian_collective_population).toFixed(1)}pp collectively.
      </p>

      <div className="mt-4 space-y-3">
        {entries.map((e) => (
          <div key={e.key} className="grid grid-cols-[88px_1fr] items-center gap-3 text-xs">
            <span className="font-medium">{e.label}</span>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="w-10 font-mono text-[var(--accent)]">{e.mcda}%</span>
                <div className="h-2 flex-1 rounded bg-[var(--paper)]">
                  <div
                    className="h-2 rounded bg-[var(--accent)]"
                    style={{ width: `${(e.mcda / max) * 100}%` }}
                  />
                </div>
              </div>
              <div className="flex items-center gap-2 text-[var(--muted)]">
                <span className="w-10 font-mono">{e.pop}%</span>
                <div className="h-2 flex-1 rounded bg-[var(--paper)]">
                  <div
                    className="h-2 rounded bg-[var(--muted)]/40"
                    style={{ width: `${(e.pop / max) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-4 font-mono text-[10px] uppercase text-[var(--muted)]">
        <span className="text-[var(--accent)]">■</span> MCDA-7 &nbsp;
        <span className="text-[var(--muted)]">■</span> Population baseline
      </p>
    </section>
  );
}
