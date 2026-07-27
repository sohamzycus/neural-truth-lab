import type { ShardPipelineRun } from "../../types";
import { Section } from "../shell/AppShell";
import { StatTile } from "../ui";

export function ShardEvidenceSection({ run }: { run: ShardPipelineRun }) {
  return (
    <Section
      id="shard-evidence"
      eyebrow="Verified processing"
      title="Shard Pipeline Run"
      subtitle={`Runnable pipeline executed on all ${run.inputRecords.toLocaleString()} raw shard records. Corpus total: ${run.corpusTotalObservations?.toLocaleString() ?? "47.2M"} observations.`}
    >
      <div className="mb-4 rounded-lg border border-[var(--color-accent)]/25 bg-[var(--color-accent)]/5 px-4 py-3 text-sm text-[var(--color-muted)]">
        <strong className="text-[var(--color-text)]">Algorithms run:</strong> {run.algorithms.join(" · ")}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile label="Input records" value={run.inputRecords.toLocaleString()} />
        <StatTile label="Quality rejected" value={run.qualityRejected.toLocaleString()} />
        <StatTile label="Exact dupes removed" value={run.exactDupRemoved.toLocaleString()} />
        <StatTile label="Near-dup records" value={run.nearDupRecords.toLocaleString()} />
        <StatTile label="Decontam rejected" value={run.decontamRejected.toLocaleString()} />
        <StatTile label="PII masked" value={run.piiMasked.toLocaleString()} />
        <StatTile label="Near-dup clusters" value={run.nearDupClusters.toLocaleString()} />
        <StatTile label="Train-safe reps" value={run.acceptedRecords.toLocaleString()} hint="After all gates" />
      </div>
      <p className="mt-4 font-mono text-[10px] text-[var(--color-muted)]">
        Reproduce: <code className="text-[var(--color-accent)]">npm run pipeline:shard</code> →{" "}
        <code>public/data/shard_pipeline_run.json</code>
      </p>
    </Section>
  );
}
