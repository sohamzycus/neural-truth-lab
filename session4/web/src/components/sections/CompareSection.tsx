import { useEffect, useMemo, useState } from "react";
import type { Comparison, ScrubSample } from "../../types";
import { exactHash } from "../../lib/scrub";
import { setBenchmarkPhrases, runPipeline, type PipelineResult } from "../../lib/pipeline/runPipeline";
import { Section } from "../shell/AppShell";
import { BeforeAfter } from "../ui";

export function CompareSection({
  comparisons,
  samples,
  quizPhrases,
}: {
  comparisons: Comparison[];
  samples: ScrubSample[];
  quizPhrases: string[];
}) {
  const [cmpId, setCmpId] = useState(comparisons[0]?.id ?? "");
  const [sampleId, setSampleId] = useState(samples[0]?.id ?? "");
  const [pipeline, setPipeline] = useState<PipelineResult | null>(null);
  const cmp = comparisons.find((c) => c.id === cmpId) ?? comparisons[0];
  const sample = samples.find((s) => s.id === sampleId) ?? samples[0];

  useEffect(() => {
    setBenchmarkPhrases(quizPhrases);
  }, [quizPhrases]);

  useEffect(() => {
    if (!sample) return;
    let cancelled = false;
    runPipeline(sample.id, sample.text, exactHash).then((r) => {
      if (!cancelled) setPipeline(r);
    });
    return () => {
      cancelled = true;
    };
  }, [sample]);

  const transforms = useMemo(
    () => pipeline?.steps.map((s) => `${s.stage}${s.ok ? "" : " ✗"}`) ?? [],
    [pipeline],
  );

  return (
    <Section
      id="compare"
      eyebrow="Transformation"
      title="Before / After Comparison"
      subtitle="Curated surgery on the left. Live pipeline playground runs all implemented stages in-browser."
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
        <h3 className="text-xl font-medium">Pipeline playground</h3>
        <p className="mt-2 max-w-2xl text-sm text-[var(--color-muted)]">
          Runs scrub → quality filter → script language ID → MinHash signature → SHA-256 exact hash →
          13-gram benchmark decontamination on sample notes.
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
        {sample && pipeline ? (
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="panel p-4">
              <div className="mb-2 text-[11px] uppercase tracking-wider text-[var(--color-danger)]">Input</div>
              <pre className="whitespace-pre-wrap font-mono text-xs text-[var(--color-muted)]">{sample.text}</pre>
            </div>
            <div className="panel p-4">
              <div className="mb-2 flex items-center justify-between gap-2">
                <span className="text-[11px] uppercase tracking-wider text-[var(--color-ok)]">Pipeline output</span>
                <span
                  className={`font-mono text-[10px] uppercase ${pipeline.accepted ? "text-[var(--color-ok)]" : "text-[var(--color-warn)]"}`}
                >
                  {pipeline.accepted ? "train-safe" : "rejected"}
                </span>
              </div>
              <pre className="whitespace-pre-wrap font-mono text-xs">{pipeline.cleanText}</pre>
              <ul className="mt-4 space-y-1 text-xs">
                {pipeline.steps.map((s) => (
                  <li key={s.stage} className={s.ok ? "text-[var(--color-accent)]" : "text-[var(--color-warn)]"}>
                    {s.stage}: {s.detail}
                  </li>
                ))}
              </ul>
              {transforms.length ? (
                <div className="mt-4 flex flex-wrap gap-1.5">
                  {transforms.map((t) => (
                    <span key={t} className="rounded border border-[var(--color-border)] px-2 py-0.5 font-mono text-[9px]">
                      {t}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </Section>
  );
}
