import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Download, FileJson, FileText, Search } from "lucide-react";
import type { RawObservation } from "../../types";
import { downloadText } from "../../lib/download";
import { Section } from "../shell/AppShell";
import { ObservationCard } from "../ui";
import { IngestionTicker } from "../ui/IngestionTicker";

const PAGE_SIZE = 12;

function toJsonl(observations: RawObservation[]) {
  return observations.map((o) => JSON.stringify(o)).join("\n");
}

export function RawSection({
  data,
  totalCorpus,
}: {
  data: RawObservation[];
  totalCorpus: number;
}) {
  const [page, setPage] = useState(0);
  const [query, setQuery] = useState("");
  const [issueFilter, setIssueFilter] = useState<string | null>(null);

  const allIssues = useMemo(() => [...new Set(data.flatMap((o) => o.issues))].sort(), [data]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return data.filter((o) => {
      if (issueFilter && !o.issues.includes(issueFilter)) return false;
      if (!q) return true;
      return (
        o.text.toLowerCase().includes(q) ||
        o.title.toLowerCase().includes(q) ||
        o.meta?.species?.toLowerCase().includes(q) ||
        o.meta?.location?.toLowerCase().includes(q)
      );
    });
  }, [data, query, issueFilter]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, pageCount - 1);
  const slice = filtered.slice(safePage * PAGE_SIZE, safePage * PAGE_SIZE + PAGE_SIZE);

  const downloadJson = () => downloadText("raw_observations_shard.json", JSON.stringify(data, null, 2));
  const downloadJsonl = () =>
    downloadText("raw_observations_shard.jsonl", toJsonl(data), "application/x-ndjson;charset=utf-8");
  const downloadManifest = () => {
    const manifest = {
      corpusVersion: "ataavi-text-v0.4",
      totalObservations: totalCorpus,
      shardRecords: data.length,
      exportedAt: new Date().toISOString(),
      format: "json",
    };
    downloadText("corpus_manifest.json", JSON.stringify(manifest, null, 2));
  };

  return (
    <Section
      id="raw"
      eyebrow="The problem"
      title="Raw Observation Viewer"
      subtitle={`Noisy community notes at corpus scale — ${totalCorpus.toLocaleString()} observations ingested. Browse, filter, and download the ${data.length.toLocaleString()}-record sample shard.`}
    >
      <IngestionTicker observations={data} totalCorpus={totalCorpus} label="Ingestion queue" />

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={downloadJson}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-text)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
        >
          <FileJson className="h-3.5 w-3.5" />
          Download shard JSON ({data.length.toLocaleString()})
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
          onClick={downloadManifest}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-xs font-medium text-[var(--color-muted)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
        >
          <Download className="h-3.5 w-3.5" />
          Corpus manifest
        </button>
      </div>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--color-muted)]" />
          <input
            type="search"
            value={query}
            aria-label="Search observations"
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(0);
            }}
            placeholder="Search species, location, note text…"
            className="w-full rounded-lg border border-[var(--color-border)] bg-black/25 py-2 pl-9 pr-3 text-sm text-[var(--color-text)] outline-none transition focus:border-[var(--color-accent)]/50"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => {
              setIssueFilter(null);
              setPage(0);
            }}
            className={`rounded-full border px-2.5 py-1 text-[10px] font-mono uppercase tracking-wide transition ${
              issueFilter === null
                ? "border-[var(--color-accent)] bg-[var(--color-accent)]/15 text-[var(--color-accent)]"
                : "border-[var(--color-border)] text-[var(--color-muted)] hover:text-[var(--color-text)]"
            }`}
          >
            All
          </button>
          {allIssues.map((issue) => (
            <button
              key={issue}
              type="button"
              onClick={() => {
                setIssueFilter(issue);
                setPage(0);
              }}
              className={`rounded-full border px-2.5 py-1 text-[10px] font-mono uppercase tracking-wide transition ${
                issueFilter === issue
                  ? "border-[var(--color-warn)] bg-[var(--color-warn)]/10 text-[var(--color-warn)]"
                  : "border-[var(--color-border)] text-[var(--color-muted)] hover:text-[var(--color-text)]"
              }`}
            >
              {issue}
            </button>
          ))}
        </div>
      </div>

      <p className="mt-3 text-xs text-[var(--color-muted)]">
        Showing {slice.length} of {filtered.length.toLocaleString()} matching · shard{" "}
        {data.length.toLocaleString()} of {totalCorpus.toLocaleString()} corpus records
      </p>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {slice.map((o, i) => (
          <motion.div
            key={o.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
          >
            <ObservationCard title={o.title} issues={o.issues} text={o.text} meta={o.meta} />
          </motion.div>
        ))}
      </div>

      {pageCount > 1 ? (
        <div className="mt-8 flex items-center justify-center gap-4">
          <button
            type="button"
            disabled={safePage === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-border)] px-3 py-2 text-xs text-[var(--color-muted)] transition enabled:hover:border-[var(--color-accent)]/40 enabled:hover:text-[var(--color-accent)] disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
            Prev
          </button>
          <span className="font-mono text-xs text-[var(--color-muted)]">
            Page {safePage + 1} / {pageCount}
          </span>
          <button
            type="button"
            disabled={safePage >= pageCount - 1}
            onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            className="inline-flex items-center gap-1 rounded-lg border border-[var(--color-border)] px-3 py-2 text-xs text-[var(--color-muted)] transition enabled:hover:border-[var(--color-accent)]/40 enabled:hover:text-[var(--color-accent)] disabled:opacity-40"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      ) : null}
    </Section>
  );
}
