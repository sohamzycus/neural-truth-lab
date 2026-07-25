import { motion } from "framer-motion";
import type { DatasetStats } from "../../types";
import { Section } from "../shell/AppShell";
import { AnimatedCount } from "../ui/AnimatedCount";
import { StatTile } from "../ui";

function AnimatedStatTile({
  label,
  value,
  numeric,
  compact,
  hint,
}: {
  label: string;
  value?: string;
  numeric?: number;
  compact?: boolean;
  hint?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.4 }}
      className="panel p-4 transition hover:border-[var(--color-accent)]/25"
    >
      <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-muted)]">{label}</div>
      <div className="mt-2 font-mono text-2xl tracking-tight text-[var(--color-text)]">
        {numeric !== undefined ? <AnimatedCount value={numeric} compact={compact} /> : value}
      </div>
      {hint ? <div className="mt-1 text-sm text-[var(--color-muted)]">{hint}</div> : null}
    </motion.div>
  );
}

export function DatasetSection({ data }: { data: DatasetStats }) {
  return (
    <Section
      id="dataset"
      eyebrow="Source corpus"
      title="Dataset Explorer"
      subtitle={`${data.name} — ${data.inspiredBy}`}
    >
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[var(--color-accent)]/30 bg-[var(--color-accent)]/10 px-3 py-1">
        <span className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-accent)]">
          {data.rawShardRecords?.toLocaleString() ?? "—"}-record live shard ·{" "}
          <AnimatedCount value={data.observationCount} compact /> total
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <AnimatedStatTile label="Observations" numeric={data.observationCount} compact />
        <AnimatedStatTile label="Countries" numeric={data.countries} />
        <AnimatedStatTile label="Languages" numeric={data.languages} />
        <AnimatedStatTile label="Species" numeric={data.species} compact />
        <AnimatedStatTile label="Years" value={data.observationYears} />
        <AnimatedStatTile label="Avg note length" value={`${data.averageNoteLength} tokens`} />
        <AnimatedStatTile label="Observers" numeric={data.observerCount} compact />
        <StatTile label="Focus" value="India-primary" hint="Thin global slice for decontamination" />
      </div>

      <h3 className="mt-10 text-sm font-medium uppercase tracking-[0.14em] text-[var(--color-muted)]">
        Sample observations
      </h3>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {data.samples.map((s, i) => (
          <motion.div
            key={s.id}
            initial={{ opacity: 0, x: i % 2 === 0 ? -10 : 10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
            className="panel p-4 transition hover:border-[var(--color-accent)]/20"
          >
            <div className="flex items-baseline justify-between gap-2">
              <span className="font-medium">{s.species}</span>
              <span className="font-mono text-[10px] text-[var(--color-muted)]">{s.id}</span>
            </div>
            <div className="mt-1 text-xs text-[var(--color-accent)]">{s.location}</div>
            <p className="mt-3 text-sm text-[var(--color-muted)]">{s.excerpt}</p>
          </motion.div>
        ))}
      </div>
    </Section>
  );
}
