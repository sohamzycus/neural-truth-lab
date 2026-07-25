import { useMemo, useState } from "react";
import type { Comparison, ScrubSample } from "../../types";
import { scrubObservation } from "../../lib/scrub";
import { Section } from "../shell/AppShell";
import { BeforeAfter } from "../ui";

export function CompareSection({
  comparisons,
  samples,
}: {
  comparisons: Comparison[];
  samples: ScrubSample[];
}) {
  const [cmpId, setCmpId] = useState(comparisons[0]?.id ?? "");
  const [sampleId, setSampleId] = useState(samples[0]?.id ?? "");
  const cmp = comparisons.find((c) => c.id === cmpId) ?? comparisons[0];
  const sample = samples.find((s) => s.id === sampleId) ?? samples[0];
  const scrubbed = useMemo(() => (sample ? scrubObservation(sample.text) : null), [sample]);

  return (
    <Section
      id="compare"
      eyebrow="Transformation"
      title="Before / After Comparison"
      subtitle="Curated surgery on the left. Live client-side scrub playground below."
    >
      <div className="mb-4 flex flex-wrap gap-2">
        {comparisons.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setCmpId(c.id)}
            className={`rounded-md border px-3 py-1.5 text-xs transition ${
              cmpId === c.id
                ? "border-[var(--color-accent)] text-[var(--color-accent)]"
                : "border-[var(--color-border)] text-[var(--color-muted)]"
            }`}
          >
            {c.title}
          </button>
        ))}
      </div>
      {cmp ? <BeforeAfter raw={cmp.raw} clean={cmp.clean} transforms={cmp.transforms} /> : null}

      <div className="mt-12 border-t border-[var(--color-border)] pt-10">
        <h3 className="text-xl font-medium">Scrub playground</h3>
        <p className="mt-2 max-w-2xl text-sm text-[var(--color-muted)]">
          Runs Unicode NFKC, HTML strip, PII mask, and whitespace collapse in-browser on a small sample — not the full corpus.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {samples.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => setSampleId(s.id)}
              className={`rounded-md border px-3 py-1.5 text-xs ${
                sampleId === s.id
                  ? "border-[var(--color-accent)] text-[var(--color-accent)]"
                  : "border-[var(--color-border)] text-[var(--color-muted)]"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        {sample && scrubbed ? (
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="panel p-4">
              <div className="mb-2 text-[11px] uppercase tracking-wider text-[var(--color-danger)]">Input</div>
              <pre className="whitespace-pre-wrap font-mono text-xs text-[var(--color-muted)]">{sample.text}</pre>
            </div>
            <div className="panel p-4">
              <div className="mb-2 text-[11px] uppercase tracking-wider text-[var(--color-ok)]">Output</div>
              <pre className="whitespace-pre-wrap font-mono text-xs">{scrubbed.text}</pre>
              <ul className="mt-4 space-y-1 text-xs text-[var(--color-accent)]">
                {scrubbed.steps.map((s) => (
                  <li key={s.name}>
                    {s.name}: {s.detail}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </div>
    </Section>
  );
}
