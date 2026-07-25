import type { DatasetStats } from "../../types";
import { Section } from "../shell/AppShell";
import { StatTile } from "../ui";

export function DatasetSection({ data }: { data: DatasetStats }) {
  return (
    <Section
      id="dataset"
      eyebrow="Source corpus"
      title="Dataset Explorer"
      subtitle={`${data.name} — ${data.inspiredBy}`}
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile label="Observations" value={data.observationCount.toLocaleString()} />
        <StatTile label="Countries" value={data.countries} />
        <StatTile label="Languages" value={data.languages} />
        <StatTile label="Species" value={data.species.toLocaleString()} />
        <StatTile label="Years" value={data.observationYears} />
        <StatTile label="Avg note length" value={`${data.averageNoteLength} tokens`} />
        <StatTile label="Observers" value={data.observerCount.toLocaleString()} />
        <StatTile label="Focus" value="India-primary" hint="Thin global slice for decontamination" />
      </div>
      <h3 className="mt-10 text-sm font-medium uppercase tracking-[0.14em] text-[var(--color-muted)]">
        Sample observations
      </h3>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {data.samples.map((s) => (
          <div key={s.id} className="panel p-4">
            <div className="flex items-baseline justify-between gap-2">
              <span className="font-medium">{s.species}</span>
              <span className="font-mono text-[10px] text-[var(--color-muted)]">{s.id}</span>
            </div>
            <div className="mt-1 text-xs text-[var(--color-accent)]">{s.location}</div>
            <p className="mt-3 text-sm text-[var(--color-muted)]">{s.excerpt}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
