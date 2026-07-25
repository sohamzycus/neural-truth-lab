import { Download, FileJson, FileText } from "lucide-react";
import type { RawObservation } from "../../types";
import { downloadText } from "../../lib/download";
import { Section } from "../shell/AppShell";
import { ObservationCard } from "../ui";

function toJsonl(observations: RawObservation[]) {
  return observations.map((o) => JSON.stringify(o)).join("\n");
}

export function RawSection({ data }: { data: RawObservation[] }) {
  const downloadJson = () => {
    downloadText("raw_observations.json", JSON.stringify(data, null, 2));
  };

  const downloadJsonl = () => {
    downloadText("raw_observations.jsonl", toJsonl(data), "application/x-ndjson;charset=utf-8");
  };

  const downloadStatic = () => {
    const a = document.createElement("a");
    a.href = "/data/raw_observations.json";
    a.download = "raw_observations.json";
    a.click();
  };

  return (
    <Section
      id="raw"
      eyebrow="The problem"
      title="Raw Observation Viewer"
      subtitle="Noisy community notes — the reason a cleaning pipeline exists. Download the sample shard for offline inspection or pipeline prototyping."
    >
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={downloadJson}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-text)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
        >
          <FileJson className="h-3.5 w-3.5" />
          Download JSON
        </button>
        <button
          type="button"
          onClick={downloadJsonl}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-text)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
        >
          <FileText className="h-3.5 w-3.5" />
          Download JSONL
        </button>
        <button
          type="button"
          onClick={downloadStatic}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-muted)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
        >
          <Download className="h-3.5 w-3.5" />
          Corpus manifest
        </button>
        <span className="text-xs text-[var(--color-muted)]">{data.length} observations in sample shard</span>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {data.map((o) => (
          <ObservationCard key={o.id} title={o.title} issues={o.issues} text={o.text} meta={o.meta} />
        ))}
      </div>
    </Section>
  );
}
