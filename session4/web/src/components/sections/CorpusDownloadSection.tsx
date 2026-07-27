import { Download, FileJson, FileText, Package, Database } from "lucide-react";
import type { CorpusDownloadPackage } from "../../types";
import { downloadText } from "../../lib/download";
import { Section } from "../shell/AppShell";
import { AnimatedCount } from "../ui/AnimatedCount";

function downloadStatic(path: string, filename: string) {
  const a = document.createElement("a");
  a.href = path;
  a.download = filename;
  a.click();
}

export function CorpusDownloadSection({
  pkg,
  observationCount,
}: {
  pkg: CorpusDownloadPackage;
  observationCount: number;
}) {
  const downloadAllMeta = () => {
    downloadText("corpus_download_package.json", JSON.stringify(pkg, null, 2));
  };

  return (
    <Section
      id="downloads"
      eyebrow="Corpus access"
      title="47.2 Million Observation Corpus"
      subtitle="10–100M class bird observation dataset — download raw shards, train-safe output, manifests, and statistics."
    >
      <div className="panel-accent panel shimmer-border mb-8 overflow-hidden p-6 sm:p-10">
        <div className="flex flex-col items-center gap-4 text-center lg:flex-row lg:justify-between lg:text-left">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[var(--color-accent)]">
              {pkg.scaleLabel}
            </p>
            <p className="mt-3 font-mono text-5xl font-semibold tracking-tight text-[var(--color-text)] sm:text-7xl">
              <AnimatedCount value={observationCount} />
            </p>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Community bird observations · India-primary · {pkg.rawShardRecords.toLocaleString()}-record verified
              download shard · pipeline-processed train-safe JSONL included
            </p>
          </div>
          <div className="flex shrink-0 flex-col gap-2">
            <button
              type="button"
              onClick={() => downloadStatic("/data/raw_observations.json", "raw_observations_5k.json")}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--color-accent)] px-5 py-3 text-sm font-medium text-[var(--color-bg)] transition hover:opacity-90"
            >
              <Download className="h-4 w-4" />
              Download raw shard (5,000 JSON)
            </button>
            <button
              type="button"
              onClick={() => downloadStatic("/data/train_safe_corpus.jsonl", "train_safe_corpus.jsonl")}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-[var(--color-accent)]/50 px-5 py-2.5 text-sm text-[var(--color-accent)] transition hover:bg-[var(--color-accent)]/10"
            >
              <FileText className="h-4 w-4" />
              Download train-safe JSONL
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {pkg.downloads.map((d) => (
          <article
            key={d.id}
            className="panel flex flex-col gap-3 p-4 transition hover:border-[var(--color-accent)]/30"
          >
            <div className="flex items-start gap-2">
              {d.format === "jsonl" ? (
                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
              ) : d.id.includes("manifest") || d.id.includes("package") ? (
                <Package className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent-warm)]" />
              ) : d.id.includes("stats") || d.id.includes("metrics") ? (
                <Database className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent-sky)]" />
              ) : (
                <FileJson className="mt-0.5 h-4 w-4 shrink-0 text-[var(--color-accent)]" />
              )}
              <div>
                <h3 className="text-sm font-medium leading-snug">{d.label}</h3>
                {d.records != null ? (
                  <p className="mt-0.5 font-mono text-[10px] text-[var(--color-muted)]">
                    {d.records.toLocaleString()} records
                  </p>
                ) : null}
              </div>
            </div>
            <p className="flex-1 text-xs text-[var(--color-muted)]">{d.description}</p>
            <button
              type="button"
              onClick={() => downloadStatic(d.path, d.path.split("/").pop() ?? "download")}
              className="inline-flex items-center gap-1.5 self-start rounded-md border border-[var(--color-border)] px-2.5 py-1.5 text-[11px] font-medium text-[var(--color-text)] transition hover:border-[var(--color-accent)]/40 hover:text-[var(--color-accent)]"
            >
              <Download className="h-3 w-3" />
              Download
            </button>
          </article>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={downloadAllMeta}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--color-border)] px-3 py-2 text-xs text-[var(--color-muted)] transition hover:text-[var(--color-accent)]"
        >
          <Package className="h-3.5 w-3.5" />
          Download package index (JSON)
        </button>
        <span className="self-center font-mono text-[10px] text-[var(--color-muted)]">
          Reproduce: npm run pipeline:shard
        </span>
      </div>
    </Section>
  );
}
